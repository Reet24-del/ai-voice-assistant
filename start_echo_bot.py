#!/usr/bin/env python3

"""
Simple server starter for Echo Bot v2 demo
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    print("🚀 Starting Echo Bot v2 Demo Servers")
    print("=" * 50)
    
    # Start Flask server
    print("Starting Flask frontend server...")
    flask_process = subprocess.Popen([
        sys.executable, "-c", 
        "from app import app; app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)"
    ])
    
    time.sleep(3)  # Wait for Flask to start
    
    # Start FastAPI server  
    print("Starting FastAPI backend server...")
    fastapi_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "fastapi_server:app", 
        "--host", "127.0.0.1", "--port", "8000", "--reload"
    ])
    
    print("\n✅ Servers started!")
    print("📱 Open your browser and go to: http://127.0.0.1:5000")
    print("🆕 Try the Echo Bot v2 - TTS Echo section!")
    print("\nPress Ctrl+C to stop both servers...")
    
    try:
        # Keep running until interrupted
        flask_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        try:
            flask_process.terminate()
            fastapi_process.terminate()
        except:
            pass
        print("✅ Servers stopped!")

if __name__ == "__main__":
    main()
