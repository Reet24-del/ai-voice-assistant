#!/usr/bin/env python3

"""
Simple test script for the /tts/echo endpoint
"""

import requests
import io

def test_echo_tts():
    """Test the /tts/echo endpoint with a simple audio file"""
    
    # Create a simple test audio file (empty WebM file headers)
    # This is just for testing the endpoint structure
    test_audio_data = b'dummy_audio_data'
    
    # Prepare the request
    url = "http://127.0.0.1:8000/tts/echo"
    
    files = {
        'audio_file': ('test.webm', io.BytesIO(test_audio_data), 'audio/webm')
    }
    
    data = {
        'voice_id': 'en-US-sarah',
        'speed': '100'
    }
    
    try:
        print("Testing /tts/echo endpoint...")
        response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_echo_tts()
