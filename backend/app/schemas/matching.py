"""Schemas for matching feature (groups, likes, matches)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Group Schemas
# ============================================================================

class GroupMemberResponse(BaseModel):
    """Response model for group member."""
    id: int
    user_id: int
    user_name: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class GroupCreateRequest(BaseModel):
    """Request to create a group."""
    name: Optional[str] = None
    description: Optional[str] = None
    member_ids: List[int] = Field(..., min_items=1, description="List of user IDs to add as members")


class GroupResponse(BaseModel):
    """Response model for group."""
    id: int
    name: Optional[str]
    description: Optional[str]
    created_by_id: Optional[int]
    is_active: bool
    members: List[GroupMemberResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddMemberRequest(BaseModel):
    """Request to add a member to a group."""
    user_id: int
    role: str = Field(default="member")


# ============================================================================
# Like Schemas
# ============================================================================

class LikeCreateRequest(BaseModel):
    """Request to create a like."""
    liker_group_id: int
    likee_group_id: int


class LikeResponse(BaseModel):
    """Response model for like."""
    id: int
    liker_group_id: int
    likee_group_id: int
    initiator_user_id: Optional[int]
    group_b_approvals_count: int
    group_b_required_count: int
    group_a_approvals_count: int
    group_a_required_count: int
    status: str
    matched_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApproveLikeResponse(BaseModel):
    """Response when approving a like."""
    like: LikeResponse
    match: Optional["MatchResponse"] = None
    message: str = "Like approved"


# ============================================================================
# Match Schemas
# ============================================================================

class MatchResponse(BaseModel):
    """Response model for match."""
    id: int
    group1_id: int
    group2_id: int
    matched_at: datetime
    last_message_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MatchesResponse(BaseModel):
    """Response for list of matches."""
    matches: List[MatchResponse]

