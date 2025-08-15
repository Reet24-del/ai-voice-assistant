#!/usr/bin/env python3
"""
Startup script for Day 10: Chat History Voice Agent
Runs both FastAPI backend server and Flask frontend server
"""

import subprocess
import threading
import time
import sys
import signal
import webbrowser
from pathlib import Path

def run_fastapi():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server on http://127.0.0.1:8000")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "fastapi_server:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ], cwd=Path(__file__).parent, check=True)
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError as e:
        print(f"❌ FastAPI server failed: {e}")

def run_flask():
    """Run the Flask server"""
    print("🌐 Starting Flask server on http://127.0.0.1:5000")
    try:
        subprocess.run([
            sys.executable, "app.py"
        ], cwd=Path(__file__).parent, check=True)
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError as e:
        print(f"❌ Flask server failed: {e}")

def main():
    print("=" * 60)
    print("🤖 30 Days of AI Voice Agents - Day 10: Chat History")
    print("=" * 60)
    print()
    print("Starting servers...")
    print()
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Wait a moment for FastAPI to start
    time.sleep(3)
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    time.sleep(2)
    
    print("✅ Both servers are starting up...")
    print()
    print("📱 Frontend (Flask): http://127.0.0.1:5000")
    print("🔧 Backend (FastAPI): http://127.0.0.1:8000")
    print("🤖 Chat Bot: http://127.0.0.1:5000/chat")
    print()
    print("Opening chat bot in your browser...")
    
    # Open the chat bot interface
    try:
        webbrowser.open('http://127.0.0.1:5000/chat')
    except Exception as e:
        print(f"Could not open browser: {e}")
        print("Please manually open: http://127.0.0.1:5000/chat")
    
    print()
    print("🎤 Instructions:")
    print("1. Hold the microphone button and speak your message")
    print("2. Release the button when you're done speaking")
    print("3. The AI will transcribe, process, and respond with voice")
    print("4. Continue the conversation - the AI remembers context!")
    print()
    print("Press Ctrl+C to stop both servers...")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()
