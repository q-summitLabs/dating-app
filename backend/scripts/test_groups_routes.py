#!/usr/bin/env python3
"""
Test script for groups routes.

Tests:
- POST /groups (create group)
- POST /groups/{group_id}/members (add member)

Usage:
    poetry run python scripts/test_groups_routes.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import httpx
import json
from typing import Optional, Dict

BASE_URL = "http://localhost:8080"


async def login_user(client: httpx.AsyncClient, email: str, password: str) -> Optional[str]:
    """Login and return access token."""
    try:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
        )
        if response.status_code == 200:
            return response.json()["tokens"]["access_token"]
        return None
    except Exception as e:
        print(f"  Error logging in {email}: {e}")
        return None


async def test_create_group(
    client: httpx.AsyncClient,
    token: str,
    name: str,
    description: str,
    member_ids: list = None,
) -> Optional[dict]:
    """Test creating a group."""
    print(f"\n👥 Testing POST /groups")
    print(f"   Name: {name}")
    print(f"   Description: {description}")
    print(f"   Member IDs: {member_ids or []}")
    
    try:
        response = await client.post(
            f"{BASE_URL}/groups",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": name,
                "description": description,
                "member_ids": member_ids or [],
            },
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✓ Group created successfully")
            print(f"   Group ID: {data['id']}")
            print(f"   Created by: {data['created_by_id']}")
            print(f"   Members: {len(data['members'])}")
            for member in data['members']:
                print(f"     - {member['user_name']} (ID: {member['user_id']}, Role: {member['role']})")
            return data
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get('detail', response.text[:200])
            print(f"   ✗ Failed to create group: {detail}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")
        return None


async def test_add_member(
    client: httpx.AsyncClient,
    token: str,
    group_id: int,
    user_id: int,
    role: str = "member",
) -> Optional[dict]:
    """Test adding a member to a group."""
    print(f"\n➕ Testing POST /groups/{group_id}/members")
    print(f"   User ID: {user_id}")
    print(f"   Role: {role}")
    
    try:
        response = await client.post(
            f"{BASE_URL}/groups/{group_id}/members",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": user_id,
                "role": role,
            },
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✓ Member added successfully")
            print(f"   Member ID: {data['id']}")
            print(f"   User: {data['user_name']} (ID: {data['user_id']})")
            print(f"   Role: {data['role']}")
            print(f"   Joined at: {data['joined_at']}")
            return data
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get('detail', response.text[:200])
            print(f"   ✗ Failed to add member: {detail}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")
        return None


async def test_create_group_unauthorized(client: httpx.AsyncClient):
    """Test creating a group without authentication."""
    print(f"\n🚫 Testing POST /groups without authentication")
    
    try:
        response = await client.post(
            f"{BASE_URL}/groups",
            json={
                "name": "Unauthorized Group",
                "description": "Should fail",
                "member_ids": [],
            },
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"   ✓ Correctly rejected unauthorized request")
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")


async def get_user_id_from_email(client: httpx.AsyncClient, token: str) -> Optional[int]:
    """Get current user ID from token (by making a request that returns user info)."""
    # We can't easily get user ID from token without decoding it
    # So we'll use a workaround: try to create a group and see the created_by_id
    # Or we can get it from login response
    return None


async def find_users_from_db() -> Dict[str, int]:
    """Find existing users from database."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from app.core.config import settings
    from app.models.user import User
    
    engine = create_async_engine(settings.async_database_url, echo=False)
    users = {}
    
    try:
        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(User).where(User.email.in_([
                    "brad@example.com",
                    "david@example.com",
                    "becca@example.com",
                    "chelsea@example.com",
                    "alex@example.com",
                    "sam@example.com",
                ]))
            )
            user_list = result.scalars().all()
            
            for user in user_list:
                users[user.email] = user.id
                
    except Exception as e:
        print(f"  Error finding users: {e}")
    finally:
        await engine.dispose()
    
    return users


async def run_tests():
    """Run all groups route tests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Check if server is running
            try:
                await client.get(f"{BASE_URL}/ping")
            except Exception:
                print("❌ Error: Server is not running!")
                print("   Please start the server first:")
                print("   poetry run uvicorn app.main:app --reload")
                return
            
            print("=" * 60)
            print("GROUPS ROUTES TEST SUITE")
            print("=" * 60)
            print("✓ Server is running\n")
            
            # Find existing users
            print("Finding existing users...")
            users = await find_users_from_db()
            
            if not users:
                print("❌ No users found!")
                print("   Please run reset_users.py first:")
                print("   poetry run python scripts/reset_users.py")
                return
            
            print(f"✓ Found {len(users)} users:")
            for email, user_id in users.items():
                print(f"   {email}: ID {user_id}")
            
            # Login as first user
            print("\n" + "=" * 60)
            print("AUTHENTICATION")
            print("=" * 60)
            
            test_email = "brad@example.com"
            print(f"Logging in as {test_email}...")
            token = await login_user(client, test_email, "password123456")
            
            if not token:
                print("❌ Failed to login. Make sure users exist.")
                print("   Run: poetry run python scripts/reset_users.py")
                return
            
            print(f"✓ Logged in successfully\n")
            
            # Get user IDs for testing
            brad_id = users.get("brad@example.com")
            david_id = users.get("david@example.com")
            becca_id = users.get("becca@example.com")
            
            # Test 1: Create group
            print("=" * 60)
            print("TEST 1: CREATE GROUP")
            print("=" * 60)
            group_result = await test_create_group(
                client,
                token,
                name="Test Group",
                description="A test group for API testing",
                member_ids=[brad_id] if brad_id else [],
            )
            
            if not group_result:
                print("\n⚠️  Could not create group. Check error above.")
                return
            
            group_id = group_result['id']
            creator_id = group_result['created_by_id']
            
            # Test 2: Add member to group
            if david_id and david_id != creator_id:
                print("\n" + "=" * 60)
                print("TEST 2: ADD MEMBER")
                print("=" * 60)
                await test_add_member(
                    client,
                    token,
                    group_id,
                    david_id,
                    role="member",
                )
            
            # Test 3: Try to add member when not in group (should fail)
            if becca_id:
                print("\n" + "=" * 60)
                print("TEST 3: ADD MEMBER (UNAUTHORIZED)")
                print("=" * 60)
                print("   Testing adding member as non-member user...")
                
                # Login as different user who is not in the group
                becca_token = await login_user(client, "becca@example.com", "password123456")
                if becca_token:
                    # This should fail because becca is not a member
                    result = await test_add_member(
                        client,
                        becca_token,
                        group_id,
                        becca_id,
                        role="member",
                    )
                    if not result:
                        print("   ✓ Correctly rejected (user not a member of group)")
            
            # Test 4: Create group with multiple members
            print("\n" + "=" * 60)
            print("TEST 4: CREATE GROUP WITH MEMBERS")
            print("=" * 60)
            if brad_id and david_id:
                await test_create_group(
                    client,
                    token,
                    name="Test Group with Members",
                    description="A group created with multiple members",
                    member_ids=[brad_id, david_id],
                )
            
            # Test 5: Unauthorized access
            print("\n" + "=" * 60)
            print("TEST 5: UNAUTHORIZED ACCESS")
            print("=" * 60)
            await test_create_group_unauthorized(client)
            
            # Summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print("✓ Create group endpoint tested")
            print("✓ Add member endpoint tested")
            print("✓ Error handling tested")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_tests())

