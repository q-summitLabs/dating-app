from __future__ import annotations

from typing import Annotated
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import AuthUser, User
from app.schemas.photo import (
    PhotoUploadResponse,
    PhotoDeleteResponse,
    PhotosUpdateResponse,
)
from app.services.s3 import s3_service

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/upload", response_model=PhotoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PhotoUploadResponse:
    """
    Upload a photo for the current user.

    - Validates image format and size
    - Uploads to S3
    - Returns the public URL
    """
    user_id = str(current_user.user_id)

    # Upload to S3
    s3_key, url = await s3_service.upload_photo(file, user_id)

    # Update user's pictures array
    user = current_user.profile
    if user.pictures is None:
        user.pictures = []
    user.pictures.append(url)
    await db.commit()
    await db.refresh(user)

    return PhotoUploadResponse(url=url, s3_key=s3_key)


@router.delete("/", response_model=PhotoDeleteResponse)
async def delete_photo(
    photo_url: Annotated[str, Query(..., description="URL of the photo to delete")],
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PhotoDeleteResponse:
    """
    Delete a photo for the current user.

    - Removes photo from S3
    - Removes URL from user's pictures array
    """
    user = current_user.profile

    # Check if photo belongs to user
    if not user.pictures or photo_url not in user.pictures:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found.",
        )

    # Extract S3 key from URL
    # URL formats:
    # - https://bucket.s3.region.amazonaws.com/photos/user_id/photo_id.ext
    # - https://s3.region.amazonaws.com/bucket/photos/user_id/photo_id.ext
    # - endpoint_url/bucket/photos/user_id/photo_id.ext
    # - endpoint_url/photos/user_id/photo_id.ext (if bucket is in path)
    try:
        parsed = urlparse(photo_url)
        path = parsed.path.lstrip("/")
        
        # Find the photos prefix in the path
        if "photos/" in path:
            # Extract everything from "photos/" onwards
            photos_idx = path.index("photos/")
            s3_key = path[photos_idx:]
        else:
            # Fallback: assume the last 3 parts are photos/user_id/photo_id.ext
            parts = path.split("/")
            if len(parts) >= 3:
                s3_key = "/".join(parts[-3:])
            else:
                raise ValueError("Invalid photo URL format: cannot extract S3 key")

        # Delete from S3
        await s3_service.delete_photo(s3_key)

        # Remove from user's pictures array
        user.pictures = [p for p in user.pictures if p != photo_url]
        await db.commit()

        return PhotoDeleteResponse()

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete photo: {str(exc)}",
        ) from exc


@router.get("/", response_model=PhotosUpdateResponse)
async def get_user_photos(
    current_user: Annotated[AuthUser, Depends(get_current_user)],
) -> PhotosUpdateResponse:
    """
    Get all photos for the current user.
    """
    user = current_user.profile
    pictures = user.pictures or []
    return PhotosUpdateResponse(pictures=pictures)


@router.put("/", response_model=PhotosUpdateResponse)
async def update_user_photos(
    picture_urls: list[str],
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PhotosUpdateResponse:
    """
    Update the user's photos list (reorder or remove photos).

    - Validates that all URLs belong to the user
    - Updates the pictures array
    """
    user = current_user.profile
    current_pictures = user.pictures or []

    # Validate that all provided URLs are in the user's current photos
    invalid_urls = [url for url in picture_urls if url not in current_pictures]
    if invalid_urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid photo URLs: {', '.join(invalid_urls)}",
        )

    # Update pictures array
    user.pictures = picture_urls
    await db.commit()
    await db.refresh(user)

    return PhotosUpdateResponse(pictures=user.pictures)

