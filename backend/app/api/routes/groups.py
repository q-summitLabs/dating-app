"""Routes for group management."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.matching import Group, GroupMember
from app.models.user import AuthUser, User
from app.schemas.matching import (
    AddMemberRequest,
    GroupCreateRequest,
    GroupMemberResponse,
    GroupResponse,
)
from app.services.matching import matching_service

router = APIRouter(prefix="/groups", tags=["groups"])


def _group_to_response(group: Group) -> GroupResponse:
    """Convert Group model to response schema."""
    members = []
    for member in group.members:
        if member.is_active:
            # Get user name - handle case where user might not be loaded
            user_name = "Unknown"
            if hasattr(member, 'user') and member.user:
                user_name = member.user.name
            elif member.user_id:
                # If user not loaded, we'll need to fetch it or use a default
                # For now, use a placeholder
                user_name = f"User {member.user_id}"

            members.append(
                GroupMemberResponse(
                    id=member.id,
                    user_id=member.user_id,
                    user_name=user_name,
                    role=member.role,
                    joined_at=member.joined_at,
                )
            )

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_by_id=group.created_by_id,
        is_active=group.is_active,
        members=members,
        created_at=group.created_at,
        updated_at=group.updated_at,
    )


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupCreateRequest,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GroupResponse:
    """
    Create a new group and add members.

    - Requires authentication
    - Creator is automatically added as a member
    - All specified member_ids are added to the group
    """
    # Ensure creator is in member list
    member_ids = list(set(payload.member_ids))  # Remove duplicates
    if current_user.user_id not in member_ids:
        member_ids.append(current_user.user_id)

    group = await matching_service.create_group(
        db=db,
        name=payload.name,
        description=payload.description,
        member_ids=member_ids,
        created_by_id=current_user.user_id,
    )

    # Load members with user data
    await db.refresh(group, attribute_names=["members"])
    result = await db.execute(
        select(Group)
        .where(Group.id == group.id)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
    )
    group = result.scalar_one()

    return _group_to_response(group)


@router.post(
    "/{group_id}/members",
    response_model=GroupMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    group_id: int,
    payload: AddMemberRequest,
    current_user: Annotated[AuthUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GroupMemberResponse:
    """
    Add a member to a group.

    - Requires authentication
    - User must be a member of the group (for now - can add permissions later)
    """
    # Verify current user is a member of the group
    membership = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.user_id,
            GroupMember.is_active == True,
        )
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of the group to add members.",
        )

    member = await matching_service.add_member_to_group(
        db=db,
        group_id=group_id,
        user_id=payload.user_id,
        role=payload.role,
    )

    # Load user data
    await db.refresh(member, attribute_names=["user"])

    return GroupMemberResponse(
        id=member.id,
        user_id=member.user_id,
        user_name=member.user.name if member.user else "Unknown",
        role=member.role,
        joined_at=member.joined_at,
    )

