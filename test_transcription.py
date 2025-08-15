#!/usr/bin/env python3
"""
Test script for the transcription endpoint
"""
import requests
import io
import wave
import struct
import math

def generate_test_audio():
    """Generate a simple test audio file in memory"""
    # Audio parameters
    sample_rate = 44100
    duration = 2  # seconds
    frequency = 440  # A4 note
    
    # Generate sine wave
    samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        sample = int(32767 * math.sin(2 * math.pi * frequency * t))
        samples.append(sample)
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))
    
    buffer.seek(0)
    return buffer

def test_transcription_endpoint():
    """Test the /transcribe/file endpoint"""
    print("Testing transcription endpoint...")
    
    # Generate test audio
    audio_buffer = generate_test_audio()
    
    # Prepare the request
    files = {
        'audio_file': ('test_audio.wav', audio_buffer, 'audio/wav')
    }
    
    try:
        # Send request to transcription endpoint
        response = requests.post('http://127.0.0.1:8000/transcribe/file', files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("✅ Transcription endpoint is working!")
                print(f"Transcription: {data['transcription']}")
            else:
                print("❌ Transcription failed")
        else:
            print(f"❌ Request failed with status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure FastAPI server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    test_transcription_endpoint()
