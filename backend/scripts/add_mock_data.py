#!/usr/bin/env python3
"""
Script to add mock data to the database for testing.

This script uses the API endpoints to create data, which ensures
all business logic and validations are applied.

Usage:
    poetry run python scripts/add_mock_data.py
"""

import asyncio
import httpx
import json
from typing import Dict, Optional

BASE_URL = "http://localhost:8080"


async def signup_user(client: httpx.AsyncClient, name: str, email: str) -> Optional[str]:
    """Sign up a user and return their access token."""
    try:
        response = await client.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "password123456",
                "name": name,
            },
        )
        if response.status_code == 201:
            data = response.json()
            return data["tokens"]["access_token"]
        elif response.status_code == 400:
            # User might already exist, try to login
            try:
                error_data = response.json()
                detail = error_data.get('detail', '')
                print(f"    Signup failed: {detail}")
            except:
                pass
            login_response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": email, "password": "password123456"},
            )
            if login_response.status_code == 200:
                print(f"    User exists, logged in instead")
                return login_response.json()["tokens"]["access_token"]
            else:
                try:
                    login_error = login_response.json().get('detail', '')
                    print(f"    Login also failed: {login_error}")
                except:
                    print(f"    Login failed with status {login_response.status_code}")
        else:
            # Show error details for any other status
            try:
                error_data = response.json()
                detail = error_data.get('detail', response.text)
                print(f"    Error ({response.status_code}): {detail}")
            except:
                print(f"    Error ({response.status_code}): {response.text[:200]}")
        return None
    except Exception as e:
        print(f"  Exception signing up {name}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def create_group(client: httpx.AsyncClient, token: str, name: str, description: str) -> Optional[int]:
    """Create a group and return its ID."""
    try:
        response = await client.post(
            f"{BASE_URL}/groups",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": name, "description": description, "member_ids": []},
        )
        if response.status_code == 201:
            return response.json()["id"]
        return None
    except Exception as e:
        print(f"  Error creating group {name}: {e}")
        return None


async def create_like(client: httpx.AsyncClient, token: str, liker_group_id: int, likee_group_id: int) -> Optional[int]:
    """Create a like and return its ID."""
    try:
        response = await client.post(
            f"{BASE_URL}/matching/likes",
            headers={"Authorization": f"Bearer {token}"},
            json={"liker_group_id": liker_group_id, "likee_group_id": likee_group_id},
        )
        if response.status_code == 201:
            return response.json()["id"]
        return None
    except Exception as e:
        print(f"  Error creating like: {e}")
        return None


async def create_mock_data():
    """Create mock users, groups, and matches using the API."""
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
            print("✓ Server is running\n")
            
            # Create users
            print("Creating users...")
            users_data = [
                {"name": "Brad", "email": "brad@example.com"},
                {"name": "David", "email": "david@example.com"},
                {"name": "Becca", "email": "becca@example.com"},
                {"name": "Chelsea", "email": "chelsea@example.com"},
                {"name": "Alex", "email": "alex@example.com"},
                {"name": "Sam", "email": "sam@example.com"},
            ]
            
            tokens = {}
            for user_data in users_data:
                token = await signup_user(client, user_data["name"], user_data["email"])
                if token:
                    tokens[user_data["name"]] = token
                    print(f"  ✓ {user_data['name']} ({user_data['email']})")
                else:
                    print(f"  ✗ Failed to create {user_data['name']}")
            
            print(f"\n✓ Created {len(tokens)} users\n")
            
            if len(tokens) < 2:
                print("❌ Need at least 2 users to create groups. Exiting.")
                return
            
            # Create groups
            print("Creating groups...")
            groups_data = [
                {
                    "name": "Brad & David Crew",
                    "description": "Weekend warriors",
                    "creator": "Brad",
                },
                {
                    "name": "Becca & Chelsea",
                    "description": "Adventure seekers",
                    "creator": "Becca",
                },
                {
                    "name": "Alex & Sam",
                    "description": "Foodies",
                    "creator": "Alex",
                },
            ]
            
            groups = {}
            for group_data in groups_data:
                creator_token = tokens.get(group_data["creator"])
                if not creator_token:
                    print(f"  ✗ Skipping {group_data['name']} - creator not found")
                    continue
                
                group_id = await create_group(
                    client, creator_token, group_data["name"], group_data["description"]
                )
                if group_id:
                    groups[group_data["name"]] = group_id
                    print(f"  ✓ {group_data['name']} (ID: {group_id})")
                else:
                    print(f"  ✗ Failed to create {group_data['name']}")
            
            print(f"\n✓ Created {len(groups)} groups\n")
            
            # Create a like
            if "Brad & David Crew" in groups and "Becca & Chelsea" in groups:
                print("Creating like...")
                brad_token = tokens.get("Brad")
                if brad_token:
                    like_id = await create_like(
                        client,
                        brad_token,
                        groups["Brad & David Crew"],
                        groups["Becca & Chelsea"],
                    )
                    if like_id:
                        print(f"  ✓ Group {groups['Brad & David Crew']} likes Group {groups['Becca & Chelsea']} (Like ID: {like_id})")
                    else:
                        print("  ✗ Failed to create like")
            
            # Summary
            print("\n" + "=" * 50)
            print("Mock data summary:")
            print(f"  Users: {len(tokens)}")
            print(f"  Groups: {len(groups)}")
            print("=" * 50)
            print("\nYou can now test the API with these users:")
            for user_data in users_data:
                print(f"  Email: {user_data['email']}, Password: password123456")
            print("\nExample: Get token and create a group")
            print('  TOKEN=$(curl -s -X POST "http://localhost:8080/auth/login" \\')
            print('    -H "Content-Type: application/json" \\')
            print('    -d \'{"email":"brad@example.com","password":"password123"}\' \\')
            print('    | jq -r \'.tokens.access_token\')')
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(create_mock_data())

