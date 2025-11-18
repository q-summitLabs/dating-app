"""
Matching Models - Group-Based Matching System

This file contains all database models for the matching feature:
- Group: Groups of users
- GroupMember: Junction table (users ↔ groups)
- Like: Group-to-group likes with approval tracking
- Match: Finalized matches between groups

All models are kept together since they're tightly related to the matching feature.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    CheckConstraint,
    Index,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.models.user import Base


# ============================================================================
# GROUPS TABLE
# ============================================================================

class Group(Base):
    """
    Groups represent a collection of users who want to match together.
    
    Example: "Brad & David's Crew" is a group with 2 members.
    
    Why a separate table?
    - Groups can have metadata (name, description, photos)
    - Groups can exist independently of users
    - Makes it easy to query "all groups" or "groups a user is in"
    """
    __tablename__ = "groups"
    __table_args__ = {"schema": "yolk_staging"}

    id = Column(Integer, primary_key=True, index=True)
    
    # Optional: Group name/description
    name = Column(String, nullable=True)  # e.g., "Weekend Warriors"
    description = Column(String, nullable=True)
    
    # Who created this group (useful for permissions later)
    created_by_id = Column(
        Integer,
        ForeignKey("yolk_staging.users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Status tracking
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    
    # Timestamps (always good to track when things were created/updated)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships (SQLAlchemy magic - makes querying easier)
    # This lets you do: group.members to get all members
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    created_by = relationship("User", foreign_keys=[created_by_id])


# ============================================================================
# GROUP MEMBERS TABLE (Junction Table)
# ============================================================================

class GroupMember(Base):
    """
    This is a "junction table" - it connects Users to Groups.
    
    Why do we need this?
    - One user can be in multiple groups (many-to-many relationship)
    - One group has multiple users (many-to-many relationship)
    - Junction tables are the standard way to handle many-to-many
    
    Example:
    - User "Brad" is in Group 1 (Brad & David)
    - User "Brad" is also in Group 5 (Brad's other crew)
    - This table stores both relationships
    
    Design decisions:
    - UNIQUE constraint: Prevents adding the same user to a group twice
    - is_active: Soft delete - user "leaves" group but we keep history
    - role: Could be 'creator', 'admin', 'member' for future features
    """
    __tablename__ = "group_members"
    __table_args__ = (
        {"schema": "yolk_staging"},
        # UNIQUE constraint: Can't add same user to same group twice
        UniqueConstraint('group_id', 'user_id', name='uq_group_member'),
        # Index for fast "find all groups for a user" queries
        Index('idx_group_members_user', 'user_id'),
        # Index for fast "find all members of a group" queries
        Index('idx_group_members_group', 'group_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys - links to groups and users tables
    group_id = Column(
        Integer,
        ForeignKey("yolk_staging.groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("yolk_staging.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Optional: Role in the group (for future features like admin permissions)
    role = Column(String, nullable=False, server_default=text("'member'"))
    
    # Soft delete - user "leaves" but we keep the record
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    
    # When they joined
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User")


# ============================================================================
# LIKES TABLE (The Heart of Matching)
# ============================================================================

class Like(Base):
    """
    This table stores when one group likes another group.
    
    Your flow:
    1. Brad (from Group A) likes Group B (Becca & Chelsea)
    2. Becca and Chelsea both approve
    3. David (Brad's group mate) approves
    4. Match is created!
    
    DENORMALIZATION EXPLAINED:
    Instead of counting approvals every time (slow), we store the counts:
    - group_b_approvals_count: How many people in Group B said yes
    - group_b_required_count: How many people in Group B need to say yes
    - Same for Group A
    
    This is "denormalized" because we're storing calculated data.
    Why? Speed! We can check "is everyone approved?" in 1 query instead of 3.
    
    Status values:
    - 'pending_group_b': Waiting for Group B to approve
    - 'pending_group_a': Waiting for Group A to approve  
    - 'matched': Everyone approved, match created
    - 'rejected': Someone rejected
    - 'expired': Approval timeout
    """
    __tablename__ = "likes"
    __table_args__ = (
        {"schema": "yolk_staging"},
        # Can't like the same group twice
        UniqueConstraint('liker_group_id', 'likee_group_id', name='uq_like'),
        # Index for "who did this group like?"
        Index('idx_likes_liker', 'liker_group_id', 'status'),
        # Index for "who liked this group?"
        Index('idx_likes_likee', 'likee_group_id', 'status'),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Which group is doing the liking
    liker_group_id = Column(
        Integer,
        ForeignKey("yolk_staging.groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Which group is being liked
    likee_group_id = Column(
        Integer,
        ForeignKey("yolk_staging.groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Who initiated the like (useful for notifications)
    initiator_user_id = Column(
        Integer,
        ForeignKey("yolk_staging.users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # DENORMALIZED: Approval tracking (stored counts for speed)
    # Group B (the liked group) approval tracking
    group_b_approvals_count = Column(Integer, nullable=False, server_default=text("0"))
    group_b_required_count = Column(Integer, nullable=False)  # Set when like is created
    
    # Group A (the liking group) approval tracking  
    group_a_approvals_count = Column(Integer, nullable=False, server_default=text("0"))
    group_a_required_count = Column(Integer, nullable=False)  # Set when like is created
    
    # Current status in the approval workflow
    status = Column(
        String,
        nullable=False,
        server_default=text("'pending_group_b'")
    )  # 'pending_group_b', 'pending_group_a', 'matched', 'rejected', 'expired'
    
    # When the match was finalized (if it becomes a match)
    matched_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    liker_group = relationship("Group", foreign_keys=[liker_group_id])
    likee_group = relationship("Group", foreign_keys=[likee_group_id])
    initiator = relationship("User", foreign_keys=[initiator_user_id])


# ============================================================================
# MATCHES TABLE (Final Matches)
# ============================================================================

class Match(Base):
    """
    This table stores final matches between groups.
    
    A match is created when:
    1. Group A likes Group B
    2. Everyone in Group B approves
    3. Everyone in Group A approves
    4. → Match created!
    
    Design decisions:
    - CHECK constraint: group1_id < group2_id prevents duplicates
      (e.g., can't have both (1,2) and (2,1) - only (1,2))
    - is_active: For "unmatching" - soft delete
    - last_message_at: For sorting matches by recent activity
    
    Why separate from likes?
    - Cleaner separation of concerns
    - Easier to query "all my matches" 
    - Can add match-specific data later (events, shared photos, etc.)
    """
    __tablename__ = "matches"
    __table_args__ = (
        {"schema": "yolk_staging"},
        # Can't match the same two groups twice
        UniqueConstraint('group1_id', 'group2_id', name='uq_match'),
        # CHECK constraint: Ensures group1_id < group2_id (prevents duplicates)
        # This means we always store (1,2) never (2,1)
        CheckConstraint('group1_id < group2_id', name='check_match_order'),
        # Index for "all matches for group 1"
        Index('idx_matches_group1', 'group1_id', 'matched_at'),
        # Index for "all matches for group 2"
        Index('idx_matches_group2', 'group2_id', 'matched_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # The two groups that matched
    # We use group1_id < group2_id to ensure consistent ordering
    group1_id = Column(
        Integer,
        ForeignKey("yolk_staging.groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group2_id = Column(
        Integer,
        ForeignKey("yolk_staging.groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # When the match was finalized
    matched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # For sorting matches by recent activity (when last message was sent)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Soft delete - groups can "unmatch"
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    group1 = relationship("Group", foreign_keys=[group1_id])
    group2 = relationship("Group", foreign_keys=[group2_id])

