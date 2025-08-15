# 🎵 Text-to-Speech Web Application

This web application allows you to convert text to speech using a web interface. It features a Flask frontend and a FastAPI backend for TTS generation.

## ✨ Features

- ✅ **Text Input**: Enter any text to convert to speech
- ✅ **Voice Selection**: Choose from different voice options (Sarah, John, Emma)
- ✅ **Speed Control**: Adjust speech speed from 50% to 150%
- ✅ **Audio Playback**: Built-in HTML5 audio player with controls
- ✅ **Responsive Design**: Works on desktop and mobile devices
- ✅ **Real-time Feedback**: Loading states and error handling

## 🏗️ Architecture

- **Frontend**: Flask web server (Port 5000) serving HTML/CSS/JavaScript
- **Backend**: FastAPI TTS service (Port 8000) with Murf API integration
- **Audio Playback**: HTML5 `<audio>` element with MP3 support

## 🚀 Quick Start

### Option 1: Start Both Servers Automatically
```bash
python start_servers.py
```

### Option 2: Start Servers Manually

1. **Start the FastAPI TTS Server** (Terminal 1):
```bash
python fastapi_server.py
```

2. **Start the Flask Web Server** (Terminal 2):
```bash
python app.py
```

3. **Open your browser** and go to: http://127.0.0.1:5000

## 🔧 Environment Setup

Make sure you have a `.env` file with your Murf API key:
```
MURF_API_KEY=your_api_key_here
```

## 📱 How to Use

1. **Enter Text**: Type or paste text into the textarea
2. **Select Voice**: Choose from the dropdown (Sarah, John, or Emma)
3. **Adjust Speed**: Use the slider to set speech speed (50-150%)
4. **Generate Speech**: Click the "Generate Speech" button
5. **Play Audio**: The audio player will appear with your generated speech
6. **Controls**: Use the audio player controls to play, pause, or scrub through the audio

## 🎯 API Endpoints

### FastAPI TTS Service (Port 8000)
- `POST /generate-tts` - Generate TTS audio
- `GET /` - API status
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Flask Web Server (Port 5000)
- `GET /` - Main web application
- `GET /api/hello` - Test API endpoint

## 🔊 Supported Features

- **Input**: Plain text (up to reasonable length limits)
- **Output**: MP3 audio files
- **Voices**: Multiple English voices (US/UK)
- **Speed**: Variable playback speed
- **Browser Support**: Modern browsers with HTML5 audio support

## 🛠️ Technical Details

### Frontend (JavaScript)
- Validates input text
- Shows loading states during API calls
- Handles errors gracefully
- Manages audio playback
- Responsive UI with Bootstrap

### Backend (FastAPI)
- Async request handling
- Input validation with Pydantic models
- Error handling and logging
- Integration with Murf TTS API
- CORS support for cross-origin requests

## 🐛 Troubleshooting

### Common Issues

1. **"MURF_API_KEY not found"**
   - Solution: Create a `.env` file with your API key

2. **"Failed to fetch"**
   - Solution: Make sure the FastAPI server is running on port 8000

3. **Audio doesn't play**
   - Solution: Check browser audio permissions and settings

4. **Connection refused**
   - Solution: Ensure both servers are running and not blocked by firewall

### Testing the Setup

1. Visit: http://127.0.0.1:8000/health (Should return "healthy")
2. Visit: http://127.0.0.1:5000 (Should load the web interface)
3. Try the "Fetch Data from API" button first to test connectivity

## 📋 Requirements

- Python 3.7+
- Flask
- FastAPI
- Uvicorn
- httpx
- python-dotenv
- pydantic
- Valid Murf API key

## 🎉 Enjoy!

Your TTS web application is now ready to use! Type some text, select a voice, and hear it come to life!
