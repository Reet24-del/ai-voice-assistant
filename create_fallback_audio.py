#!/usr/bin/env python3
"""
Fallback Audio Generator

This script creates fallback audio files for when external TTS APIs fail.
Uses Windows SAPI (Speech API) or cross-platform alternatives.
"""

import os
import sys
from pathlib import Path

def create_fallback_audio_windows():
    """Create fallback audio using Windows SAPI"""
    try:
        import win32com.client
        
        # Create the static directory if it doesn't exist
        static_dir = Path("static")
        static_dir.mkdir(exist_ok=True)
        
        # Initialize SAPI
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        
        fallback_messages = {
            "connection_issue": "I'm having trouble connecting right now. Please try again in a moment.",
            "service_unavailable": "The service is temporarily unavailable. Please try again shortly.",
            "general_error": "Something went wrong. Please try again in a moment.",
            "transcription_failed": "I couldn't understand the audio clearly. Please try speaking more clearly.",
            "llm_unavailable": "AI service is experiencing difficulties. Please try again."
        }
        
        for filename, message in fallback_messages.items():
            output_path = static_dir / f"fallback_{filename}.wav"
            
            # Create file stream
            file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
            file_stream.Open(str(output_path), 3)  # 3 = write mode
            
            # Set output to file
            speaker.AudioOutputStream = file_stream
            
            # Speak the message
            speaker.Speak(message)
            
            # Close the file stream
            file_stream.Close()
            
            print(f"✅ Created: {output_path}")
        
        return True
        
    except ImportError:
        print("⚠️ pywin32 not available. Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Error creating Windows SAPI audio: {str(e)}")
        return False

def create_fallback_audio_pyttsx3():
    """Create fallback audio using pyttsx3 (cross-platform)"""
    try:
        import pyttsx3
        
        # Create the static directory if it doesn't exist
        static_dir = Path("static")
        static_dir.mkdir(exist_ok=True)
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Set properties (optional)
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)  # Use first available voice
        
        engine.setProperty('rate', 150)  # Speed
        engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        fallback_messages = {
            "connection_issue": "I'm having trouble connecting right now. Please try again in a moment.",
            "service_unavailable": "The service is temporarily unavailable. Please try again shortly.",
            "general_error": "Something went wrong. Please try again in a moment.",
            "transcription_failed": "I couldn't understand the audio clearly. Please try speaking more clearly.",
            "llm_unavailable": "AI service is experiencing difficulties. Please try again."
        }
        
        for filename, message in fallback_messages.items():
            output_path = static_dir / f"fallback_{filename}.wav"
            
            # Save to file
            engine.save_to_file(message, str(output_path))
            engine.runAndWait()
            
            print(f"✅ Created: {output_path}")
        
        return True
        
    except ImportError:
        print("⚠️ pyttsx3 not available. Install with: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"❌ Error creating pyttsx3 audio: {str(e)}")
        return False

def create_simple_tone_files():
    """Create simple tone files as a last resort"""
    try:
        import numpy as np
        import scipy.io.wavfile as wavfile
        
        # Create the static directory if it doesn't exist
        static_dir = Path("static")
        static_dir.mkdir(exist_ok=True)
        
        # Generate a simple pleasant tone (C major chord)
        sample_rate = 44100
        duration = 2.0  # 2 seconds
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create a pleasant chord (C4 + E4 + G4)
        freq_c = 261.63  # C4
        freq_e = 329.63  # E4
        freq_g = 392.00  # G4
        
        # Generate the chord with fade in/out
        tone = (np.sin(2 * np.pi * freq_c * t) + 
                np.sin(2 * np.pi * freq_e * t) + 
                np.sin(2 * np.pi * freq_g * t)) / 3
        
        # Add fade in/out to avoid clicks
        fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
        tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
        tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        # Normalize and convert to 16-bit
        tone = np.int16(tone * 32767 * 0.3)  # 30% volume
        
        # Save tone files
        tone_files = [
            "fallback_connection_issue.wav",
            "fallback_service_unavailable.wav", 
            "fallback_general_error.wav",
            "fallback_transcription_failed.wav",
            "fallback_llm_unavailable.wav"
        ]
        
        for filename in tone_files:
            output_path = static_dir / filename
            wavfile.write(str(output_path), sample_rate, tone)
            print(f"✅ Created tone file: {output_path}")
        
        return True
        
    except ImportError:
        print("⚠️ numpy/scipy not available. Install with: pip install numpy scipy")
        return False
    except Exception as e:
        print(f"❌ Error creating tone files: {str(e)}")
        return False

def main():
    print("🎵 Fallback Audio Generator")
    print("=" * 40)
    
    # Try different methods in order of preference
    methods = [
        ("Windows SAPI", create_fallback_audio_windows),
        ("pyttsx3 (cross-platform)", create_fallback_audio_pyttsx3),
        ("Simple tones", create_simple_tone_files)
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔄 Trying {method_name}...")
        if method_func():
            print(f"✅ Successfully created fallback audio files using {method_name}")
            return True
        else:
            print(f"❌ {method_name} failed, trying next method...")
    
    print("\n❌ All methods failed. You may need to install dependencies:")
    print("   pip install pywin32 pyttsx3 numpy scipy")
    return False

if __name__ == "__main__":
    main()
