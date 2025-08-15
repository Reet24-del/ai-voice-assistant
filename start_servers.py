#!/usr/bin/env python3
"""
Start both Flask and FastAPI servers for the TTS web application
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_server(script_name, port, server_name):
    """Start a server in a separate process"""
    try:
        print(f"🚀 Starting {server_name} on port {port}...")
        process = subprocess.Popen([
            sys.executable, script_name
        ], cwd=Path(__file__).parent)
        return process
    except Exception as e:
        print(f"❌ Failed to start {server_name}: {e}")
        return None

def main():
    print("=" * 60)
    print("🎵 TTS Web Application Server Starter")
    print("=" * 60)
    
    # Check if required files exist
    flask_app = Path("app.py")
    fastapi_app = Path("fastapi_server.py")
    
    if not flask_app.exists():
        print("❌ Flask app (app.py) not found!")
        return
        
    if not fastapi_app.exists():
        print("❌ FastAPI server (fastapi_server.py) not found!")
        return
    
    print("✅ Found Flask app and FastAPI server")
    print()
    
    # Start both servers
    flask_process = start_server("app.py", 5000, "Flask Server")
    time.sleep(2)  # Give Flask time to start
    
    fastapi_process = start_server("fastapi_server.py", 8000, "FastAPI TTS Server")
    
    if flask_process and fastapi_process:
        print()
        print("✅ Both servers started successfully!")
        print()
        print("📱 Access your web application at: http://127.0.0.1:5000")
        print("🔧 FastAPI TTS endpoint: http://127.0.0.1:8000/generate-tts")
        print("📚 FastAPI docs: http://127.0.0.1:8000/docs")
        print()
        print("Press Ctrl+C to stop both servers...")
        
        try:
            # Wait for user to stop
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            flask_process.terminate()
            fastapi_process.terminate()
            print("✅ Servers stopped!")
    else:
        print("❌ Failed to start one or both servers")

if __name__ == "__main__":
    main()
