#!/usr/bin/env python3
"""
Start Flask and Mock FastAPI servers for testing TTS functionality without real API key
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_server(script_name, port, server_name):
    """Start a server in a separate process"""
    try:
        print(f"Starting {server_name} on port {port}...")
        process = subprocess.Popen([
            sys.executable, script_name
        ], cwd=Path(__file__).parent)
        return process
    except Exception as e:
        print(f"Failed to start {server_name}: {e}")
        return None

def main():
    print("=" * 70)
    print("TTS Web Application - TEST MODE (Mock Server)")
    print("=" * 70)
    print("This uses a mock TTS server for testing the UI functionality")
    print("No Murf API key required - returns sample audio for testing")
    print()
    
    # Check if required files exist
    flask_app = Path("app.py")
    mock_fastapi_app = Path("fastapi_server_mock.py")
    
    if not flask_app.exists():
        print("ERROR: Flask app (app.py) not found!")
        return
        
    if not mock_fastapi_app.exists():
        print("ERROR: Mock FastAPI server (fastapi_server_mock.py) not found!")
        return
    
    print("Found Flask app and Mock FastAPI server")
    print()
    
    # Start both servers
    flask_process = start_server("app.py", 5000, "Flask Server")
    time.sleep(2)  # Give Flask time to start
    
    fastapi_process = start_server("fastapi_server_mock.py", 8000, "Mock FastAPI TTS Server")
    
    if flask_process and fastapi_process:
        print()
        print("Both servers started successfully!")
        print()
        print("TEST MODE - Using Mock TTS Server")
        print("Access your web application at: http://127.0.0.1:5000")
        print("Mock TTS endpoint: http://127.0.0.1:8000/generate-tts")
        print("API docs: http://127.0.0.1:8000/docs")
        print()
        print("How to test:")
        print("   1. Go to http://127.0.0.1:5000")
        print("   2. Try the TTS feature with any text")
        print("   3. It will return a sample bell sound for testing")
        print()
        print("To use real TTS:")
        print("   1. Get a Murf API key")
        print("   2. Add it to your .env file")
        print("   3. Use 'python start_servers.py' instead")
        print()
        print("Press Ctrl+C to stop both servers...")
        
        try:
            # Wait for user to stop
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping servers...")
            flask_process.terminate()
            fastapi_process.terminate()
            print("Servers stopped!")
    else:
        print("Failed to start one or both servers")

if __name__ == "__main__":
    main()
