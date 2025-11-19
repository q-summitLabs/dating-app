#!/usr/bin/env python3
"""
Reset or create users with correct passwords.

Usage:
    poetry run python scripts/reset_users.py
"""

import asyncio
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User, AuthUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def reset_users():
    """Update or create test users with correct passwords."""
    engine = create_async_engine(settings.async_database_url, echo=False)
    
    async with AsyncSession(engine) as session:
        try:
            users_data = [
                {"name": "Brad", "email": "brad@example.com", "phone": "555-0001"},
                {"name": "David", "email": "david@example.com", "phone": "555-0002"},
                {"name": "Becca", "email": "becca@example.com", "phone": "555-0003"},
                {"name": "Chelsea", "email": "chelsea@example.com", "phone": "555-0004"},
                {"name": "Alex", "email": "alex@example.com", "phone": "555-0005"},
                {"name": "Sam", "email": "sam@example.com", "phone": "555-0006"},
            ]
            
            print("Updating/Creating test users...")
            password_hash = hash_password("password123456")
            
            for user_data in users_data:
                # Check if user exists
                result = await session.execute(
                    select(User).where(User.email == user_data["email"])
                )
                user = result.scalar_one_or_none()
                
                if user:
                    # Update existing user
                    user.name = user_data["name"]
                    user.phone_number = user_data["phone"]
                    if not user.interests:
                        user.interests = ["hiking", "travel", "food"]
                    if not user.location:
                        user.location = "San Francisco, CA"
                    
                    # Update auth_user password
                    auth_result = await session.execute(
                        select(AuthUser).where(AuthUser.user_id == user.id)
                    )
                    auth_user = auth_result.scalar_one_or_none()
                    if auth_user:
                        auth_user.password_hash = password_hash
                        auth_user.is_active = True
                        print(f"  ✓ Updated {user_data['name']} (password reset)")
                    else:
                        # Create auth_user if missing
                        auth_user = AuthUser(
                            email=user_data["email"],
                            password_hash=password_hash,
                            user_id=user.id,
                            is_active=True,
                        )
                        session.add(auth_user)
                        print(f"  ✓ Updated {user_data['name']} (added auth)")
                else:
                    # Create new user
                    user = User(
                        name=user_data["name"],
                        email=user_data["email"],
                        phone_number=user_data["phone"],
                        interests=["hiking", "travel", "food"],
                        location="San Francisco, CA",
                    )
                    session.add(user)
                    await session.flush()  # Get the user ID
                    
                    # Create auth_user
                    auth_user = AuthUser(
                        email=user_data["email"],
                        password_hash=password_hash,
                        user_id=user.id,
                        is_active=True,
                    )
                    session.add(auth_user)
                    print(f"  ✓ Created {user_data['name']} ({user_data['email']})")
            
            await session.commit()
            print(f"\n✓ Processed {len(users_data)} users")
            print("\nAll users have password: password123456")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_users())

