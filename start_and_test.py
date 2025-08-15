#!/usr/bin/env python3

"""
Complete startup and test script for Echo Bot v2 with Murf AI integration
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_servers():
    """Start both Flask and FastAPI servers"""
    print("🚀 Starting Echo Bot v2 servers...")
    
    # Start FastAPI server in background
    fastapi_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "fastapi_server:app", 
        "--host", "127.0.0.1", "--port", "8000", "--reload"
    ])
    
    time.sleep(3)  # Wait for FastAPI to start
    
    # Start Flask server
    flask_process = subprocess.Popen([
        sys.executable, "-c", 
        "from app import app; app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)"
    ])
    
    return flask_process, fastapi_process

def test_system():
    """Test the complete system"""
    print("\n🧪 Testing Echo Bot v2 system...")
    
    # Test FastAPI health
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server is healthy")
        else:
            print("❌ FastAPI server health check failed")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to FastAPI server")
        return False
    
    # Test Flask server
    try:
        response = requests.get("http://127.0.0.1:5000/api/hello", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is healthy")
        else:
            print("❌ Flask server health check failed")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Flask server")
        return False
    
    # Test Murf API integration
    murf_key = os.getenv("MURF_API_KEY")
    if murf_key:
        print("✅ Murf API key is configured")
    else:
        print("❌ Murf API key is missing")
        return False
    
    # Test AssemblyAI integration
    assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
    if assemblyai_key:
        print("✅ AssemblyAI API key is configured")
    else:
        print("❌ AssemblyAI API key is missing")
        return False
    
    return True

def main():
    print("🎙️ Echo Bot v2 - Complete Setup and Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("fastapi_server.py").exists() or not Path("app.py").exists():
        print("❌ Error: Please run this script from the python-webapp directory")
        print("Current directory:", Path.cwd())
        return
    
    # Test system first
    print("📋 Checking system configuration...")
    if not test_system():
        print("\n❌ System configuration issues detected!")
        print("Please check your API keys and configurations.")
        return
    
    print("\n🚀 Starting servers...")
    
    try:
        # Start servers
        flask_proc, fastapi_proc = start_servers()
        
        # Wait for servers to fully start
        time.sleep(5)
        
        print("\n✅ Servers started successfully!")
        print("\n📱 Your Echo Bot v2 is ready!")
        print("🌐 Open your browser and go to: http://127.0.0.1:5000")
        print("🆕 Try the \"Echo Bot v2 - TTS Echo\" section!")
        print("\n🎯 Features Available:")
        print("   • Record your voice")
        print("   • Get transcription via AssemblyAI")
        print("   • Hear it back in Murf AI voices")
        print("   • Choose from 6 different voices")
        print("\n📊 API Endpoints:")
        print("   • FastAPI Docs: http://127.0.0.1:8000/docs")
        print("   • Health Check: http://127.0.0.1:8000/health")
        print("   • Echo Endpoint: http://127.0.0.1:8000/tts/echo")
        
        print("\nPress Ctrl+C to stop both servers...")
        
        # Keep running until interrupted
        flask_proc.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        try:
            flask_proc.terminate()
            fastapi_proc.terminate()
            flask_proc.wait(timeout=5)
            fastapi_proc.wait(timeout=5)
        except:
            pass
        print("✅ Servers stopped successfully!")

if __name__ == "__main__":
    main()
