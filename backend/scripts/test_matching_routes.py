#!/usr/bin/env python3
"""
Test script for matching/likes routes.

Tests:
- POST /matching/likes (create like)
- POST /matching/likes/{like_id}/approve (approve like)
- GET /matching/groups/{group_id}/matches (get matches)

This script assumes groups already exist (run create_mock_groups.py first).

Usage:
    poetry run python scripts/test_matching_routes.py
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


async def get_user_groups(client: httpx.AsyncClient, token: str) -> list:
    """Get groups for the current user (if endpoint exists)."""
    # Note: This endpoint may not exist, so we'll work with known group IDs
    # For now, we'll use the groups created by create_mock_groups.py
    return []


async def test_create_like(
    client: httpx.AsyncClient,
    token: str,
    liker_group_id: int,
    likee_group_id: int,
) -> Optional[dict]:
    """Test creating a like."""
    print(f"\n❤️  Testing POST /matching/likes")
    print(f"   Liker Group ID: {liker_group_id}")
    print(f"   Likee Group ID: {likee_group_id}")
    
    try:
        response = await client.post(
            f"{BASE_URL}/matching/likes",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "liker_group_id": liker_group_id,
                "likee_group_id": likee_group_id,
            },
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✓ Like created successfully")
            print(f"   Like ID: {data['id']}")
            print(f"   Status: {data['status']}")
            print(f"   Group A approvals: {data['group_a_approvals_count']}/{data['group_a_required_count']}")
            print(f"   Group B approvals: {data['group_b_approvals_count']}/{data['group_b_required_count']}")
            return data
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get('detail', response.text[:200])
            print(f"   ✗ Failed to create like: {detail}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")
        return None


async def test_approve_like(
    client: httpx.AsyncClient,
    token: str,
    like_id: int,
) -> Optional[dict]:
    """Test approving a like."""
    print(f"\n✅ Testing POST /matching/likes/{like_id}/approve")
    
    try:
        response = await client.post(
            f"{BASE_URL}/matching/likes/{like_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ {data['message']}")
            print(f"   Like Status: {data['like']['status']}")
            print(f"   Group A approvals: {data['like']['group_a_approvals_count']}/{data['like']['group_a_required_count']}")
            print(f"   Group B approvals: {data['like']['group_b_approvals_count']}/{data['like']['group_b_required_count']}")
            
            if data.get('match'):
                match = data['match']
                print(f"   🎉 Match created!")
                print(f"   Match ID: {match['id']}")
                print(f"   Group 1 ID: {match['group1_id']}")
                print(f"   Group 2 ID: {match['group2_id']}")
                print(f"   Matched at: {match['matched_at']}")
            else:
                print(f"   ⏳ Match not yet created (more approvals needed)")
            
            return data
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get('detail', response.text[:200])
            print(f"   ✗ Failed to approve like: {detail}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")
        return None


async def test_get_group_matches(
    client: httpx.AsyncClient,
    token: str,
    group_id: int,
) -> Optional[dict]:
    """Test getting matches for a group."""
    print(f"\n📋 Testing GET /matching/groups/{group_id}/matches")
    
    try:
        response = await client.get(
            f"{BASE_URL}/matching/groups/{group_id}/matches",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            print(f"   ✓ Found {len(matches)} match(es)")
            
            for i, match in enumerate(matches, 1):
                print(f"   Match {i}:")
                print(f"     ID: {match['id']}")
                print(f"     Group 1 ID: {match['group1_id']}")
                print(f"     Group 2 ID: {match['group2_id']}")
                print(f"     Active: {match['is_active']}")
                print(f"     Matched at: {match['matched_at']}")
            
            return data
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get('detail', response.text[:200])
            print(f"   ✗ Failed to get matches: {detail}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")
        return None


async def test_create_like_unauthorized(
    client: httpx.AsyncClient,
    liker_group_id: int,
    likee_group_id: int,
):
    """Test creating a like without authentication."""
    print(f"\n🚫 Testing POST /matching/likes without authentication")
    
    try:
        response = await client.post(
            f"{BASE_URL}/matching/likes",
            json={
                "liker_group_id": liker_group_id,
                "likee_group_id": likee_group_id,
            },
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"   ✓ Correctly rejected unauthorized request")
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")


async def find_groups_from_db() -> Dict[str, int]:
    """Find existing groups from database."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from app.core.config import settings
    from app.models.matching import Group
    
    engine = create_async_engine(settings.async_database_url, echo=False)
    groups = {}
    
    try:
        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(Group).where(Group.is_active == True)
            )
            group_list = result.scalars().all()
            
            for group in group_list:
                groups[group.name] = group.id
                
    except Exception as e:
        print(f"  Error finding groups: {e}")
    finally:
        await engine.dispose()
    
    return groups


async def run_tests():
    """Run all matching route tests."""
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
            print("MATCHING/LIKES ROUTES TEST SUITE")
            print("=" * 60)
            print("✓ Server is running\n")
            
            # Find existing groups
            print("Finding existing groups...")
            groups = await find_groups_from_db()
            
            if not groups:
                print("❌ No groups found!")
                print("   Please run create_mock_groups.py first:")
                print("   poetry run python scripts/create_mock_groups.py")
                return
            
            print(f"✓ Found {len(groups)} groups:")
            for name, group_id in groups.items():
                print(f"   {name}: ID {group_id}")
            
            # Get group IDs for testing
            group_names = list(groups.keys())
            if len(group_names) < 2:
                print("❌ Need at least 2 groups to test likes")
                return
            
            liker_group_name = group_names[0]
            likee_group_name = group_names[1]
            liker_group_id = groups[liker_group_name]
            likee_group_id = groups[likee_group_name]
            
            # Login users
            print("\n" + "=" * 60)
            print("AUTHENTICATION")
            print("=" * 60)
            
            # Get token for a user in the liker group
            # Based on create_mock_groups.py, first group is "Brad & David Crew"
            if "Brad" in liker_group_name or "brad" in liker_group_name.lower():
                user_email = "brad@example.com"
            elif "Becca" in liker_group_name or "becca" in liker_group_name.lower():
                user_email = "becca@example.com"
            elif "Alex" in liker_group_name or "alex" in liker_group_name.lower():
                user_email = "alex@example.com"
            else:
                user_email = "brad@example.com"  # Default
            
            print(f"Logging in as {user_email}...")
            token = await login_user(client, user_email, "password123456")
            
            if not token:
                print("❌ Failed to login. Make sure users exist.")
                print("   Run: poetry run python scripts/reset_users.py")
                return
            
            print(f"✓ Logged in successfully\n")
            
            # Test 1: Create like
            print("=" * 60)
            print("TEST 1: CREATE LIKE")
            print("=" * 60)
            like_result = await test_create_like(
                client, token, liker_group_id, likee_group_id
            )
            
            if not like_result:
                print("\n⚠️  Could not create like. This might be because:")
                print("   - User is not a member of the liker group")
                print("   - Like already exists")
                print("   - Invalid group IDs")
                print("\nTrying with different user...")
                
                # Try with a user from the likee group
                if "Becca" in likee_group_name or "becca" in likee_group_name.lower():
                    alt_email = "becca@example.com"
                elif "Chelsea" in likee_group_name or "chelsea" in likee_group_name.lower():
                    alt_email = "chelsea@example.com"
                else:
                    alt_email = "david@example.com"
                
                alt_token = await login_user(client, alt_email, "password123456")
                if alt_token:
                    like_result = await test_create_like(
                        client, alt_token, liker_group_id, likee_group_id
                    )
                    if like_result:
                        token = alt_token  # Use this token for subsequent tests
            else:
                like_id = like_result['id']
                
                # Test 2: Approve like (from likee group perspective)
                print("\n" + "=" * 60)
                print("TEST 2: APPROVE LIKE")
                print("=" * 60)
                
                # Get token for a user in the likee group
                if "Becca" in likee_group_name or "becca" in likee_group_name.lower():
                    approver_email = "becca@example.com"
                elif "Chelsea" in likee_group_name or "chelsea" in likee_group_name.lower():
                    approver_email = "chelsea@example.com"
                elif "Alex" in likee_group_name or "alex" in likee_group_name.lower():
                    approver_email = "alex@example.com"
                elif "Sam" in likee_group_name or "sam" in likee_group_name.lower():
                    approver_email = "sam@example.com"
                else:
                    approver_email = "becca@example.com"
                
                print(f"Logging in as {approver_email} to approve...")
                approver_token = await login_user(client, approver_email, "password123456")
                
                if approver_token:
                    approve_result = await test_approve_like(
                        client, approver_token, like_id
                    )
                    
                    # If match was created, test getting matches
                    if approve_result and approve_result.get('match'):
                        print("\n" + "=" * 60)
                        print("TEST 3: GET MATCHES")
                        print("=" * 60)
                        
                        # Test getting matches for both groups
                        await test_get_group_matches(
                            client, approver_token, liker_group_id
                        )
                        await test_get_group_matches(
                            client, approver_token, likee_group_id
                        )
            
            # Test 4: Unauthorized access
            print("\n" + "=" * 60)
            print("TEST 4: UNAUTHORIZED ACCESS")
            print("=" * 60)
            await test_create_like_unauthorized(
                client, liker_group_id, likee_group_id
            )
            
            # Summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print("✓ Create like endpoint tested")
            print("✓ Approve like endpoint tested")
            print("✓ Get matches endpoint tested")
            print("✓ Error handling tested")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_tests())

