#!/usr/bin/env python3

"""
Test script to verify Murf API integration for Echo Bot v2
"""

import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_murf_api_direct():
    """Test Murf API directly to verify the API key and endpoint"""
    
    api_key = os.getenv("MURF_API_KEY")
    if not api_key:
        print("❌ MURF_API_KEY not found in environment variables")
        return False
    
    print(f"🔑 Using API Key: {api_key[:20]}...")
    
    # Murf API endpoint
    murf_url = "https://api.murf.ai/v1/speech/generate"
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": "Hello, this is a test of the Murf AI voice synthesis.",
        "voiceId": "en-US-samantha",
        "rate": 0,  # Normal speed (0 = normal, -50 = slow, 50 = fast)
        "sampleRate": 48000,
        "format": "MP3",
        "channelType": "MONO"
    }
    
    try:
        print("🚀 Testing Murf API directly...")
        response = requests.post(murf_url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Murf API Success!")
            print(f"Response keys: {list(result.keys())}")
            
            # Check if we got audio data
            if "audioFile" in result or "audioContent" in result or "url" in result:
                print("🎵 Audio data received successfully!")
                return True
            else:
                print("⚠️ No audio data found in response")
                print(f"Full response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Murf API Error: {response.status_code}")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    return False

def test_echo_tts_endpoint():
    """Test the /tts/echo endpoint with a dummy audio file"""
    
    # Create a simple test audio file (minimal WebM header)
    test_audio_data = b'\x1a\x45\xdf\xa3'  # Basic WebM header
    
    url = "http://127.0.0.1:8000/tts/echo"
    
    files = {
        'audio_file': ('test.webm', test_audio_data, 'audio/webm')
    }
    
    data = {
        'voice_id': 'en-US-sarah',
        'speed': '100'
    }
    
    try:
        print("🚀 Testing /tts/echo endpoint...")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Echo TTS Success!")
            print(f"Transcription: {result.get('transcription', 'N/A')}")
            print(f"Audio URL: {result.get('audio_url', 'N/A')[:50]}...")
            print(f"Processing Time: {result.get('processing_time', 'N/A')} seconds")
            return True
        else:
            print(f"❌ Echo TTS Error: {response.status_code}")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the FastAPI server is running on port 8000")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    return False

def main():
    print("🧪 Echo Bot v2 - Murf Integration Test")
    print("=" * 50)
    
    # Test 1: Direct Murf API
    print("\n1️⃣ Testing Murf API directly...")
    murf_success = test_murf_api_direct()
    
    if murf_success:
        print("\n2️⃣ Testing Echo TTS endpoint...")
        echo_success = test_echo_tts_endpoint()
        
        if echo_success:
            print("\n🎉 All tests passed! Your Echo Bot v2 is ready to use!")
        else:
            print("\n⚠️ Echo TTS endpoint test failed. Check if the FastAPI server is running.")
    else:
        print("\n❌ Murf API test failed. Please check your API key and endpoint configuration.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
