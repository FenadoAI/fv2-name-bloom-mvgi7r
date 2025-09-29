#!/usr/bin/env python3

import requests
import json
import sys

# Test the child name generator API
API_BASE = "http://localhost:8001"

def test_api_endpoints():
    """Test all the API endpoints for the child name generator"""

    print("🧪 Testing Child Name Generator API...")
    print("=" * 50)

    # Test 1: Basic health check
    try:
        response = requests.get(f"{API_BASE}/api/")
        print(f"✅ Health check: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test 2: User registration
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123"
    }

    try:
        response = requests.post(f"{API_BASE}/api/auth/register", json=test_user)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User registration: {user_data['email']}")
        else:
            print(f"⚠️  User registration (user might exist): {response.status_code}")
    except Exception as e:
        print(f"❌ User registration failed: {e}")
        return False

    # Test 3: User login
    try:
        response = requests.post(f"{API_BASE}/api/auth/login", json=test_user)
        if response.status_code == 200:
            login_data = response.json()
            token = login_data['access_token']
            print(f"✅ User login: Got token")

            # Headers for authenticated requests
            headers = {"Authorization": f"Bearer {token}"}

            # Test 4: Generate names
            name_request = {
                "gender": "boy",
                "count": 5,
                "style": "modern"
            }

            try:
                response = requests.post(f"{API_BASE}/api/names/generate", json=name_request)
                if response.status_code == 200:
                    names = response.json()
                    print(f"✅ Name generation: Generated {len(names)} names")
                    if names:
                        print(f"   Sample name: {names[0]['name']} ({names[0]['gender']}, {names[0]['origin']})")

                        # Test 5: Add to favorites
                        first_name_id = names[0]['id']
                        try:
                            response = requests.post(f"{API_BASE}/api/favorites/add/{first_name_id}", headers=headers)
                            if response.status_code == 200:
                                print(f"✅ Add to favorites: {names[0]['name']}")

                                # Test 6: Get favorites
                                response = requests.get(f"{API_BASE}/api/favorites", headers=headers)
                                if response.status_code == 200:
                                    favorites = response.json()
                                    print(f"✅ Get favorites: {len(favorites)} favorites")

                                    # Test 7: Create shareable list
                                    if favorites:
                                        response = requests.post(f"{API_BASE}/api/favorites/share", headers=headers)
                                        if response.status_code == 200:
                                            share_data = response.json()
                                            share_token = share_data['share_token']
                                            print(f"✅ Create shareable list: {share_data['share_url']}")

                                            # Test 8: Access shared list
                                            response = requests.get(f"{API_BASE}/api/shared/{share_token}")
                                            if response.status_code == 200:
                                                shared_names = response.json()
                                                print(f"✅ Access shared list: {len(shared_names)} shared names")
                                            else:
                                                print(f"❌ Access shared list failed: {response.status_code}")
                                        else:
                                            print(f"❌ Create shareable list failed: {response.status_code}")
                                else:
                                    print(f"❌ Get favorites failed: {response.status_code}")
                            else:
                                print(f"❌ Add to favorites failed: {response.status_code}")
                        except Exception as e:
                            print(f"❌ Add to favorites failed: {e}")
                else:
                    print(f"❌ Name generation failed: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Name generation failed: {e}")
        else:
            print(f"❌ User login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ User login failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 All API tests completed!")
    return True

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)