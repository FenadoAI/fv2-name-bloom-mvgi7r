#!/usr/bin/env python3
"""
Test script for the image generation API
"""
import requests
import json
import asyncio
import aiohttp

# Test the image generation using the MCP service directly
async def test_mcp_image_generation():
    """Test direct MCP image generation"""
    print("Testing MCP image generation...")

    async with aiohttp.ClientSession() as session:
        # Using the mcp__image__generate_image endpoint
        url = "https://mcp.codexhub.ai/image/generate"
        headers = {
            "Authorization": "Bearer sk-hp-CZebed93KYV7nKQTgxg",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": "Beautiful artistic illustration of the name 'Emma' written in elegant calligraphy, surrounded by soft pastel colors and gentle nature elements like flowers, stars, or clouds, perfect for a baby girl nursery decoration. The name should be the focal point with beautiful typography, dreamy and peaceful atmosphere, soft lighting, watercolor style",
            "aspect_ratio": "1:1",
            "megapixels": "1",
            "output_format": "webp"
        }

        try:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"Status: {response.status}")
                result = await response.text()
                print(f"Response: {result}")

                if response.status == 200:
                    data = json.loads(result)
                    if 'image_url' in data:
                        print(f"✅ Image generated successfully: {data['image_url']}")
                        return data['image_url']
                    else:
                        print(f"❌ No image_url in response: {data}")
                else:
                    print(f"❌ Request failed with status {response.status}")

        except Exception as e:
            print(f"❌ Error: {e}")

    return None

def test_backend_api():
    """Test our backend API endpoints"""
    print("\nTesting backend API...")

    # Test basic connectivity
    try:
        response = requests.get("http://localhost:8001/api/")
        print(f"✅ Backend connectivity: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return

    # Test name generation
    try:
        response = requests.post("http://localhost:8001/api/names/generate", json={
            "gender": "girl",
            "count": 1,
            "style": "modern"
        })
        print(f"✅ Name generation: {response.status_code}")
        if response.status_code == 200:
            names = response.json()
            print(f"Generated name: {names[0] if names else 'None'}")

            if names:
                name_id = names[0]['id']
                print(f"Name ID: {name_id}")

                # For image generation, we would need authentication
                # This test would need a valid JWT token
                print("⚠️  Image generation test requires authentication (JWT token)")

    except Exception as e:
        print(f"❌ Name generation failed: {e}")

async def main():
    """Run all tests"""
    print("🧪 Testing Image Generation Feature\n")

    # Test MCP directly first
    image_url = await test_mcp_image_generation()

    # Test backend API
    test_backend_api()

    print("\n✅ Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())