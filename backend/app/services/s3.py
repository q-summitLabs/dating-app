from __future__ import annotations

import asyncio
import uuid
from io import BytesIO
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import settings


class S3Service:
    """Service for handling S3 photo uploads and operations."""

    def __init__(self):
        self._s3_client = None
        self._bucket_name = settings.s3_bucket_name

    @property
    def s3_client(self):
        """Lazy initialization of S3 client."""
        if self._s3_client is None:
            client_kwargs = {
                "region_name": settings.aws_region,
            }

            # Add credentials if provided
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
                client_kwargs["aws_secret_access_key"] = (
                    settings.aws_secret_access_key.get_secret_value()
                    if hasattr(settings.aws_secret_access_key, "get_secret_value")
                    else settings.aws_secret_access_key
                )

            # Add endpoint URL for local testing (e.g., LocalStack)
            if settings.s3_endpoint_url:
                client_kwargs["endpoint_url"] = settings.s3_endpoint_url

            self._s3_client = boto3.client("s3", **client_kwargs)
        return self._s3_client

    def _validate_image(self, file: UploadFile) -> tuple[bytes, str]:
        """Validate and process image file."""
        # Check content type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image.",
            )

        # Read file content
        content = file.file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty.",
            )

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit.",
            )

        # Validate image format and get extension
        try:
            image = Image.open(BytesIO(content))
            image.verify()  # Verify it's a valid image

            # Get format/extension
            format_map = {
                "JPEG": "jpg",
                "PNG": "png",
                "GIF": "gif",
                "WEBP": "webp",
            }
            image_format = image.format or "JPEG"
            extension = format_map.get(image_format, "jpg")

            # Reopen for processing (verify() closes the image)
            image = Image.open(BytesIO(content))

            # Resize if too large (max 2000px on longest side)
            max_dimension = 2000
            if max(image.size) > max_dimension:
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

            # Convert to RGB if necessary (for JPEG)
            if extension == "jpg" and image.mode != "RGB":
                image = image.convert("RGB")

            # Save optimized image
            output = BytesIO()
            image.save(output, format=image_format, optimize=True, quality=85)
            content = output.getvalue()

        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image file: {str(exc)}",
            ) from exc

        return content, extension

    def _generate_s3_key(self, user_id: str, extension: str) -> str:
        """Generate a unique S3 key for the photo."""
        photo_id = str(uuid.uuid4())
        return f"{settings.s3_photo_prefix}/{user_id}/{photo_id}.{extension}"

    async def upload_photo(
        self, file: UploadFile, user_id: str
    ) -> tuple[str, str]:
        """
        Upload a photo to S3.

        Args:
            file: The uploaded file
            user_id: The ID of the user uploading the photo

        Returns:
            Tuple of (S3 key, public URL)
        """
        if not self._bucket_name:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3 bucket not configured.",
            )

        # Validate and process image
        content, extension = self._validate_image(file)

        # Generate S3 key
        s3_key = self._generate_s3_key(user_id, extension)

        try:
            # Upload to S3 (run in thread pool to avoid blocking)
            # Note: ACL parameter removed - use bucket policy for public access instead
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self._bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=f"image/{extension}",
            )

            # Generate public URL
            if settings.s3_endpoint_url:
                # For local testing (LocalStack)
                url = f"{settings.s3_endpoint_url}/{self._bucket_name}/{s3_key}"
            else:
                # Standard S3 URL
                url = f"https://{self._bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"

            return s3_key, url

        except ClientError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload photo to S3: {str(exc)}",
            ) from exc

    async def delete_photo(self, s3_key: str) -> None:
        """
        Delete a photo from S3.

        Args:
            s3_key: The S3 key of the photo to delete
        """
        if not self._bucket_name:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3 bucket not configured.",
            )

        try:
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self._bucket_name,
                Key=s3_key,
            )
        except ClientError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete photo from S3: {str(exc)}",
            ) from exc

    async def delete_photos(self, s3_keys: list[str]) -> None:
        """
        Delete multiple photos from S3.

        Args:
            s3_keys: List of S3 keys to delete
        """
        if not self._bucket_name:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3 bucket not configured.",
            )

        if not s3_keys:
            return

        try:
            # Delete objects in batch (S3 supports up to 1000 objects per request)
            objects = [{"Key": key} for key in s3_keys]
            await asyncio.to_thread(
                self.s3_client.delete_objects,
                Bucket=self._bucket_name,
                Delete={"Objects": objects},
            )
        except ClientError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete photos from S3: {str(exc)}",
            ) from exc


s3_service = S3Service()

