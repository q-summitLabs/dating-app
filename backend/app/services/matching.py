"""Service layer for matching feature (groups, likes, matches)."""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.matching import Group, GroupMember, Like, Match
from app.models.user import User


class MatchingService:
    """Service layer handling matching-related persistence logic."""

    @staticmethod
    async def create_group(
        db: AsyncSession,
        name: Optional[str],
        description: Optional[str],
        member_ids: list[int],
        created_by_id: int,
    ) -> Group:
        """Create a group and add members."""
        # Create the group
        group = Group(
            name=name,
            description=description,
            created_by_id=created_by_id,
            is_active=True,
        )
        db.add(group)
        await db.flush()  # Get the group ID

        # Add members
        members = []
        for user_id in member_ids:
            # Verify user exists
            user = await db.get(User, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found.",
                )

            member = GroupMember(
                group_id=group.id,
                user_id=user_id,
                role="member",
                is_active=True,
            )
            members.append(member)

        db.add_all(members)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create group. User may already be in group.",
            ) from exc

        await db.refresh(group, attribute_names=["members"])
        return group

    @staticmethod
    async def add_member_to_group(
        db: AsyncSession,
        group_id: int,
        user_id: int,
        role: str = "member",
    ) -> GroupMember:
        """Add a member to a group."""
        # Verify group exists
        group = await db.get(Group, group_id)
        if not group or not group.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found.",
            )

        # Verify user exists
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        # Check if already a member
        existing = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this group.",
            )

        member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            role=role,
            is_active=True,
        )
        db.add(member)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to add member to group.",
            ) from exc

        await db.refresh(member)
        return member

    @staticmethod
    async def create_like(
        db: AsyncSession,
        liker_group_id: int,
        likee_group_id: int,
        initiator_user_id: int,
    ) -> Like:
        """Create a like between two groups."""
        # Verify groups exist
        liker_group = await db.get(Group, liker_group_id)
        likee_group = await db.get(Group, likee_group_id)

        if not liker_group or not liker_group.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liker group not found.",
            )

        if not likee_group or not likee_group.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Likee group not found.",
            )

        if liker_group_id == likee_group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A group cannot like itself.",
            )

        # Check if like already exists
        existing = await db.execute(
            select(Like).where(
                Like.liker_group_id == liker_group_id,
                Like.likee_group_id == likee_group_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Like already exists.",
            )

        # Count members in each group (for required counts)
        group_a_members = await db.execute(
            select(func.count(GroupMember.id)).where(
                GroupMember.group_id == liker_group_id,
                GroupMember.is_active == True,
            )
        )
        group_a_count = group_a_members.scalar() or 0

        group_b_members = await db.execute(
            select(func.count(GroupMember.id)).where(
                GroupMember.group_id == likee_group_id,
                GroupMember.is_active == True,
            )
        )
        group_b_count = group_b_members.scalar() or 0

        if group_a_count == 0 or group_b_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Groups must have at least one active member.",
            )

        # Create the like
        like = Like(
            liker_group_id=liker_group_id,
            likee_group_id=likee_group_id,
            initiator_user_id=initiator_user_id,
            group_b_approvals_count=0,
            group_b_required_count=group_b_count,
            group_a_approvals_count=0,
            group_a_required_count=group_a_count,
            status="pending_group_b",
        )
        db.add(like)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create like.",
            ) from exc

        await db.refresh(like)
        return like

    @staticmethod
    async def approve_like(
        db: AsyncSession,
        like_id: int,
        user_id: int,
    ) -> tuple[Like, Optional[Match]]:
        """Approve a like and check if match should be created."""
        # Get the like
        like = await db.get(Like, like_id)
        if not like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Like not found.",
            )

        if like.status in ("matched", "rejected"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Like is already {like.status}.",
            )

        # Determine which group the user is in
        user_membership = await db.execute(
            select(GroupMember).where(
                GroupMember.user_id == user_id,
                GroupMember.is_active == True,
            )
        )
        memberships = user_membership.scalars().all()

        user_group_id = None
        for membership in memberships:
            if membership.group_id == like.likee_group_id:
                user_group_id = like.likee_group_id
                break
            elif membership.group_id == like.liker_group_id:
                user_group_id = like.liker_group_id
                break

        if not user_group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of either group in this like.",
            )

        # Update approval count based on which group
        match_created = None

        if user_group_id == like.likee_group_id:
            # User is in Group B (the liked group)
            like.group_b_approvals_count += 1

            if like.group_b_approvals_count >= like.group_b_required_count:
                # All Group B approved, move to Group A
                like.status = "pending_group_a"

        elif user_group_id == like.liker_group_id:
            # User is in Group A (the liking group)
            like.group_a_approvals_count += 1

            if like.group_a_approvals_count >= like.group_a_required_count:
                # All Group A approved, check if Group B also approved
                if like.group_b_approvals_count >= like.group_b_required_count:
                    # Everyone approved - create match!
                    like.status = "matched"
                    like.matched_at = func.now()

                    # Create match (ensure group1_id < group2_id)
                    group1_id = min(like.liker_group_id, like.likee_group_id)
                    group2_id = max(like.liker_group_id, like.likee_group_id)

                    match_created = Match(
                        group1_id=group1_id,
                        group2_id=group2_id,
                        matched_at=func.now(),
                        is_active=True,
                    )
                    db.add(match_created)

        await db.commit()
        await db.refresh(like)
        if match_created:
            await db.refresh(match_created)

        return like, match_created

    @staticmethod
    async def get_group_matches(
        db: AsyncSession,
        group_id: int,
    ) -> list[Match]:
        """Get all active matches for a group."""
        # Verify group exists
        group = await db.get(Group, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found.",
            )

        # Get matches where group is either group1 or group2
        result = await db.execute(
            select(Match).where(
                ((Match.group1_id == group_id) | (Match.group2_id == group_id)),
                Match.is_active == True,
            ).order_by(Match.matched_at.desc())
        )
        return list(result.scalars().all())


matching_service = MatchingService()

