#!/usr/bin/env python3
"""
Test script for authentication routes.

Tests:
- POST /auth/signup
- POST /auth/login
- POST /auth/token/refresh

Usage:
    poetry run python scripts/test_auth_routes.py
"""

import asyncio
import httpx
import json
from typing import Optional

BASE_URL = "http://localhost:8080"


async def test_signup(client: httpx.AsyncClient, name: str, email: str, password: str) -> Optional[dict]:
    """Test user signup."""
    print(f"\n📝 Testing POST /auth/signup")
    print(f"   Name: {name}, Email: {email}")
    
    try:
        response = await client.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": password,
                "name": name,
            },
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✓ Signup successful")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Access token: {data['tokens']['access_token'][:20]}...")
            print(f"   Refresh token: {data['tokens']['refresh_token'][:20]}...")
            return data
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get('detail', response.text[:500])
            if response.status_code == 500:
                print(f"   ✗ Signup failed (500): {detail}")
                print(f"   Full response: {response.text[:500]}")
            else:
                print(f"   ✗ Signup failed: {detail}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")
        return None


async def test_login(client: httpx.AsyncClient, email: str, password: str) -> Optional[dict]:
    """Test user login."""
    print(f"\n🔐 Testing POST /auth/login")
    print(f"   Email: {email}")
    
    try:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Login successful")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Access token: {data['tokens']['access_token'][:20]}...")
            print(f"   Refresh token: {data['tokens']['refresh_token'][:20]}...")
            return data
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get('detail', response.text[:500])
            if response.status_code == 500:
                print(f"   ✗ Login failed (500): {detail}")
                print(f"   Full response: {response.text[:500]}")
            else:
                print(f"   ✗ Login failed: {detail}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")
        return None


async def test_token_refresh(client: httpx.AsyncClient, refresh_token: str) -> Optional[dict]:
    """Test token refresh."""
    print(f"\n🔄 Testing POST /auth/token/refresh")
    print(f"   Refresh token: {refresh_token[:20]}...")
    
    try:
        response = await client.post(
            f"{BASE_URL}/auth/token/refresh",
            json={"refresh_token": refresh_token},
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Token refresh successful")
            print(f"   New access token: {data['access_token'][:20]}...")
            print(f"   New refresh token: {data['refresh_token'][:20]}...")
            return data
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get('detail', response.text[:200])
            print(f"   ✗ Token refresh failed: {detail}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")
        return None


async def test_invalid_login(client: httpx.AsyncClient):
    """Test login with invalid credentials."""
    print(f"\n🚫 Testing POST /auth/login with invalid credentials")
    
    try:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"},
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"   ✓ Correctly rejected invalid credentials")
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")


async def test_invalid_refresh_token(client: httpx.AsyncClient):
    """Test token refresh with invalid token."""
    print(f"\n🚫 Testing POST /auth/token/refresh with invalid token")
    
    try:
        response = await client.post(
            f"{BASE_URL}/auth/token/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"   ✓ Correctly rejected invalid refresh token")
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {e}")


async def run_tests():
    """Run all auth route tests."""
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
            print("AUTH ROUTES TEST SUITE")
            print("=" * 60)
            print("✓ Server is running\n")
            
            # Test 1: Signup new user
            test_email = "test_auth@example.com"
            test_password = "testpassword123456"
            signup_result = await test_signup(
                client, "Test User", test_email, test_password
            )
            
            # Test 2: Login with existing user (or the one we just created)
            login_result = await test_login(client, test_email, test_password)
            
            # Test 3: Token refresh (if we have a refresh token)
            if login_result and login_result.get("tokens", {}).get("refresh_token"):
                refresh_token = login_result["tokens"]["refresh_token"]
                refresh_result = await test_token_refresh(client, refresh_token)
                
                # Test 4: Use new access token from refresh
                if refresh_result:
                    print(f"\n✓ New access token obtained: {refresh_result['access_token'][:20]}...")
            
            # Test 5: Invalid login
            await test_invalid_login(client)
            
            # Test 6: Invalid refresh token
            await test_invalid_refresh_token(client)
            
            # Test 7: Login with existing test user (brad@example.com)
            print(f"\n📋 Testing login with existing test user...")
            existing_login = await test_login(client, "brad@example.com", "password123456")
            if existing_login and existing_login.get("tokens", {}).get("refresh_token"):
                await test_token_refresh(client, existing_login["tokens"]["refresh_token"])
            
            # Summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print("✓ Signup endpoint tested")
            print("✓ Login endpoint tested")
            print("✓ Token refresh endpoint tested")
            print("✓ Error handling tested")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_tests())

