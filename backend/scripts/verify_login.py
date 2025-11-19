#!/usr/bin/env python3
"""
Quick script to verify login endpoint is working after server restart.

Usage:
    poetry run python scripts/verify_login.py
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8080"


async def verify_login():
    """Verify login endpoint works."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Check server is running
            ping = await client.get(f"{BASE_URL}/ping")
            if ping.status_code != 200:
                print("❌ Server is not responding correctly")
                return False
            print("✓ Server is running")
            
            # Test login
            print("\nTesting login...")
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": "brad@example.com", "password": "password123456"},
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Login successful!")
                print(f"  User: {data['user']['name']} ({data['user']['email']})")
                print(f"  Token: {data['tokens']['access_token'][:30]}...")
                return True
            else:
                print(f"✗ Login failed with status {response.status_code}")
                try:
                    error = response.json()
                    print(f"  Error: {error.get('detail', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
                return False
                
        except httpx.ConnectError:
            print("❌ Cannot connect to server. Is it running?")
            print("   Start it with: poetry run uvicorn app.main:app --reload")
            return False
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(verify_login())
    exit(0 if success else 1)

