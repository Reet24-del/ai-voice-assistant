@echo off
echo Starting Echo Bot v2 Demo Servers...
echo ====================================

echo Starting Flask server...
start "Flask Server" python app.py

timeout /t 5 > nul

echo Starting FastAPI server...
start "FastAPI Server" python -m uvicorn fastapi_server:app --host 127.0.0.1 --port 8000 --reload

echo.
echo ✅ Servers started in separate windows!
echo 📱 Open your browser and go to: http://127.0.0.1:5000
echo 🆕 Try the Echo Bot v2 - TTS Echo section!
echo.
echo Close the server windows to stop the servers.
pause
