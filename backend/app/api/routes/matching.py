"""Routes for matching feature (likes and matches)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import AuthUser
from app.schemas.matching import (
    ApproveLikeResponse,
    LikeCreateRequest,
    LikeResponse,
    MatchResponse,
    MatchesResponse,
)
from app.services.matching import matching_service

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("/likes", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def create_like(
    payload: LikeCreateRequest,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LikeResponse:
    """
    Create a like (one group likes another group).

    - Requires authentication
    - Current user must be a member of the liker group
    - Automatically sets required approval counts based on group sizes
    """
    # Verify user is in the liker group
    from sqlalchemy import select
    from app.models.matching import GroupMember

    membership = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == payload.liker_group_id,
            GroupMember.user_id == current_user.user_id,
            GroupMember.is_active == True,
        )
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of the liker group.",
        )

    like = await matching_service.create_like(
        db=db,
        liker_group_id=payload.liker_group_id,
        likee_group_id=payload.likee_group_id,
        initiator_user_id=current_user.user_id,
    )

    return LikeResponse(
        id=like.id,
        liker_group_id=like.liker_group_id,
        likee_group_id=like.likee_group_id,
        initiator_user_id=like.initiator_user_id,
        group_b_approvals_count=like.group_b_approvals_count,
        group_b_required_count=like.group_b_required_count,
        group_a_approvals_count=like.group_a_approvals_count,
        group_a_required_count=like.group_a_required_count,
        status=like.status,
        matched_at=like.matched_at,
        created_at=like.created_at,
        updated_at=like.updated_at,
    )


@router.post(
    "/likes/{like_id}/approve",
    response_model=ApproveLikeResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_like(
    like_id: int,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApproveLikeResponse:
    """
    Approve a like.

    - Requires authentication
    - Current user must be a member of one of the groups in the like
    - Automatically creates a match if all approvals are complete
    """
    like, match = await matching_service.approve_like(
        db=db,
        like_id=like_id,
        user_id=current_user.user_id,
    )

    like_response = LikeResponse(
        id=like.id,
        liker_group_id=like.liker_group_id,
        likee_group_id=like.likee_group_id,
        initiator_user_id=like.initiator_user_id,
        group_b_approvals_count=like.group_b_approvals_count,
        group_b_required_count=like.group_b_required_count,
        group_a_approvals_count=like.group_a_approvals_count,
        group_a_required_count=like.group_a_required_count,
        status=like.status,
        matched_at=like.matched_at,
        created_at=like.created_at,
        updated_at=like.updated_at,
    )

    match_response = None
    if match:
        match_response = MatchResponse(
            id=match.id,
            group1_id=match.group1_id,
            group2_id=match.group2_id,
            matched_at=match.matched_at,
            last_message_at=match.last_message_at,
            is_active=match.is_active,
            created_at=match.created_at,
            updated_at=match.updated_at,
        )

    message = "Match created!" if match else "Like approved"

    return ApproveLikeResponse(
        like=like_response,
        match=match_response,
        message=message,
    )


@router.get(
    "/groups/{group_id}/matches",
    response_model=MatchesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_group_matches(
    group_id: int,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MatchesResponse:
    """
    Get all active matches for a group.

    - Requires authentication
    - Returns matches where the group is either group1 or group2
    """
    matches = await matching_service.get_group_matches(db=db, group_id=group_id)

    match_responses = [
        MatchResponse(
            id=match.id,
            group1_id=match.group1_id,
            group2_id=match.group2_id,
            matched_at=match.matched_at,
            last_message_at=match.last_message_at,
            is_active=match.is_active,
            created_at=match.created_at,
            updated_at=match.updated_at,
        )
        for match in matches
    ]

    return MatchesResponse(matches=match_responses)

