#!/usr/bin/env python3

"""
Fetch available voices from Murf API
"""

import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_murf_voices():
    """Get available voices from Murf API"""
    
    api_key = os.getenv("MURF_API_KEY")
    if not api_key:
        print("❌ MURF_API_KEY not found in environment variables")
        return
    
    # Murf API endpoint for voices
    murf_url = "https://api.murf.ai/v1/speech/voices"
    
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        print("🚀 Fetching available voices from Murf API...")
        response = requests.get(murf_url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully fetched voices!")
            
            # Print formatted voice list
            if 'voices' in result:
                voices = result['voices']
                print(f"\n📋 Available Voices ({len(voices)} total):")
                print("-" * 60)
                
                for voice in voices:
                    voice_id = voice.get('voice_id', 'N/A')
                    name = voice.get('name', 'N/A')
                    gender = voice.get('gender', 'N/A')
                    language = voice.get('language', 'N/A')
                    accent = voice.get('accent', 'N/A')
                    
                    print(f"ID: {voice_id:<20} | {name:<12} | {gender:<6} | {language} ({accent})")
                
                # Create a mapping for our application
                print(f"\n🔧 Suggested voice mapping for your application:")
                english_voices = [v for v in voices if v.get('language', '').startswith('en')]
                
                if english_voices:
                    print("voice_mapping = {")
                    for i, voice in enumerate(english_voices[:6]):  # Limit to 6 voices
                        voice_id = voice.get('voice_id', '')
                        name = voice.get('name', '')
                        gender = voice.get('gender', '')
                        accent = voice.get('accent', '')
                        key = f"en-{accent}-{name.lower()}" if accent else f"en-US-{name.lower()}"
                        print(f"    \"{key}\": \"{voice_id}\",")
                    print("}")
                
            else:
                print("⚠️ No voices found in response")
                print(f"Full response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Murf API Error: {response.status_code}")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    get_murf_voices()
