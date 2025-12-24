#!/usr/bin/env python3
"""
Create mock groups and likes using existing users.

Usage:
    poetry run python scripts/create_mock_groups.py
"""

import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.models.user import User
from app.models.matching import Group, GroupMember, Like

async def create_mock_groups():
    """Create groups and likes using existing users."""
    engine = create_async_engine(settings.async_database_url, echo=False)
    
    async with AsyncSession(engine) as session:
        try:
            # Get existing users
            print("Finding users...")
            users_result = await session.execute(
                select(User).where(User.email.in_([
                    "brad@example.com",
                    "david@example.com",
                    "becca@example.com",
                    "chelsea@example.com",
                    "alex@example.com",
                    "sam@example.com",
                ]))
            )
            users_list = users_result.scalars().all()
            users = {u.email: u for u in users_list}
            user_ids = {email: user.id for email, user in users.items()}  # Store IDs immediately
            
            if len(users) < 2:
                print(f"❌ Need at least 2 users, found {len(users)}")
                return
            
            print(f"✓ Found {len(users)} users\n")
            
            # Create groups
            print("Creating groups...")
            groups_data = [
                {
                    "name": "Brad & David Crew",
                    "description": "Weekend warriors",
                    "creator_email": "brad@example.com",
                    "member_emails": ["brad@example.com", "david@example.com"],
                },
                {
                    "name": "Becca & Chelsea",
                    "description": "Adventure seekers",
                    "creator_email": "becca@example.com",
                    "member_emails": ["becca@example.com", "chelsea@example.com"],
                },
                {
                    "name": "Alex & Sam",
                    "description": "Foodies",
                    "creator_email": "alex@example.com",
                    "member_emails": ["alex@example.com", "sam@example.com"],
                },
            ]
            
            groups = {}
            for group_data in groups_data:
                creator = users.get(group_data["creator_email"])
                if not creator:
                    print(f"  ✗ Skipping {group_data['name']} - creator not found")
                    continue
                
                # Check if group exists
                result = await session.execute(
                    select(Group).where(Group.name == group_data["name"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    groups[group_data["name"]] = existing
                    print(f"  ✓ {group_data['name']} already exists (ID: {existing.id})")
                    continue
                
                group = Group(
                    name=group_data["name"],
                    description=group_data["description"],
                    created_by_id=creator.id,
                    is_active=True,
                )
                session.add(group)
                await session.flush()
                await session.refresh(group)  # Refresh to get the ID
                group_id = group.id
                
                # Add members
                for member_email in group_data["member_emails"]:
                    member_user = users.get(member_email)
                    if member_user:
                        # Check if member already exists
                        member_result = await session.execute(
                            select(GroupMember).where(
                                GroupMember.group_id == group_id,
                                GroupMember.user_id == member_user.id,
                            )
                        )
                        if not member_result.scalar_one_or_none():
                            member = GroupMember(
                                group_id=group_id,
                                user_id=member_user.id,
                                role="member",
                                is_active=True,
                            )
                            session.add(member)
                
                groups[group_data["name"]] = group
                print(f"  ✓ Created {group_data['name']} (ID: {group_id})")
            
            await session.commit()
            print(f"\n✓ Created/Found {len(groups)} groups\n")
            
            # Create a like
            if "Brad & David Crew" in groups and "Becca & Chelsea" in groups:
                print("Creating like...")
                group_a = groups["Brad & David Crew"]
                group_b = groups["Becca & Chelsea"]
                
                # Get IDs safely
                await session.refresh(group_a)
                await session.refresh(group_b)
                group_a_id = group_a.id
                group_b_id = group_b.id
                
                # Check if like exists
                result = await session.execute(
                    select(Like).where(
                        Like.liker_group_id == group_a_id,
                        Like.likee_group_id == group_b_id,
                    )
                )
                existing_like = result.scalar_one_or_none()
                
                if existing_like:
                    print(f"  ✓ Like already exists (ID: {existing_like.id})")
                else:
                    # Count members
                    result_a = await session.execute(
                        select(func.count(GroupMember.id)).where(
                            GroupMember.group_id == group_a_id,
                            GroupMember.is_active == True,
                        )
                    )
                    group_a_count = result_a.scalar()
                    
                    result_b = await session.execute(
                        select(func.count(GroupMember.id)).where(
                            GroupMember.group_id == group_b_id,
                            GroupMember.is_active == True,
                        )
                    )
                    group_b_count = result_b.scalar()
                    
                    brad_id = user_ids.get("brad@example.com")
                    like = Like(
                        liker_group_id=group_a_id,
                        likee_group_id=group_b_id,
                        initiator_user_id=brad_id,
                        group_b_required_count=group_b_count,
                        group_a_required_count=group_a_count,
                        status="pending_group_b",
                    )
                    session.add(like)
                    await session.commit()
                    print(f"  ✓ Created like: Group {group_a_id} → Group {group_b_id}")
                    print(f"    Status: pending_group_b")
                    print(f"    Required: {group_b_count} from Group B, {group_a_count} from Group A")
            
            # Summary
            print("\n" + "=" * 50)
            print("Mock data summary:")
            print(f"  Users: {len(users)}")
            print(f"  Groups: {len(groups)}")
            print("=" * 50)
            print("\nTo test, use these credentials:")
            print("  Email: brad@example.com, Password: password123456")
            print("  Email: david@example.com, Password: password123456")
            print("  Email: becca@example.com, Password: password123456")
            print("  Email: chelsea@example.com, Password: password123456")
            print("  Email: alex@example.com, Password: password123456")
            print("  Email: sam@example.com, Password: password123456")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_mock_groups())

