# 🎙️ Echo Bot v2 - TTS Echo with Murf AI

A sophisticated voice echo bot that combines speech-to-text transcription with AI-powered text-to-speech synthesis.

## 🚀 Features

### Echo Bot v2 - TTS Echo (NEW!)
- **Voice Recording**: Record your voice using browser's MediaRecorder API
- **Speech-to-Text**: Transcribe audio using AssemblyAI
- **AI Voice Synthesis**: Convert transcription to speech using Murf AI voices
- **Multiple Voices**: Choose from 6 different Murf AI voices
- **Real-time Processing**: See transcription and hear AI-generated speech

### Echo Bot v1 - Audio Playback
- **Direct Playback**: Record and play back your original voice
- **Audio Upload**: Upload recorded audio to server

### Additional Features
- **Text-to-Speech**: Direct text-to-speech conversion
- **Speech-to-Text**: Standalone audio transcription
- **Responsive Design**: Works on desktop and mobile browsers

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend APIs   │    │  External APIs  │
│   (React/JS)    │◄──►│  Flask + FastAPI │◄──►│ Murf + Assembly │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Components
- **Frontend**: HTML + JavaScript + Bootstrap
- **Flask Server**: Serves web interface (Port 5000)
- **FastAPI Server**: Handles API requests (Port 8000)
- **AssemblyAI**: Speech-to-text transcription
- **Murf AI**: Text-to-speech synthesis

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge)

### 1. Install Dependencies

```bash
pip install fastapi uvicorn flask assemblyai httpx python-dotenv
```

### 2. Configure API Keys

Edit `.env` file with your API keys:
```env
# Your actual Murf AI API key
MURF_API_KEY=ap2_358dcb52-4f0c-43b6-a714-37c54fb80d9a

# Your actual AssemblyAI API key  
ASSEMBLYAI_API_KEY=c32bee36fe5447ab8ea3d28044259d84
```

### 3. Start the System

**Option A: Use the complete startup script**
```bash
cd python-webapp
python start_and_test.py
```

**Option B: Start servers manually**
```bash
# Terminal 1: Start FastAPI server
uvicorn fastapi_server:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start Flask server  
python app.py
```

### 4. Open Your Browser
Go to: **http://127.0.0.1:5000**

## 🎯 API Endpoints

### FastAPI Server (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-----------|
| `/tts/echo` | POST | **Echo Bot v2**: Transcribe audio + Generate TTS |
| `/transcribe/file` | POST | Transcribe audio file |
| `/generate-tts` | POST | Generate TTS from text |
| `/upload-audio` | POST | Upload audio file |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

### Flask Server (Port 5000)

| Endpoint | Method | Description |
|----------|--------|-----------|
| `/` | GET | Web interface |
| `/api/hello` | GET | Simple API test |

## 🎵 Available Voices

The system supports 6 Murf AI voices:

| Voice ID | Voice Name | Gender | Accent |
|----------|------------|---------|----------|
| `en-US-sarah` | Samantha | Female | US |
| `en-US-john` | Cooper | Male | US |
| `en-GB-emma` | Hazel | Female | UK |
| `en-US-david` | Daniel | Male | US |
| `en-US-jenny` | Julia | Female | US |
| `en-AU-william` | Shane | Male | Australia |

## 🧪 Testing

### Test Murf API Integration
```bash
python test_murf_integration.py
```

### Discover Available Voices
```bash
python get_murf_voices.py
```

### Manual API Testing
```bash
curl -X POST "http://127.0.0.1:8000/health"
```

## 🎉 Usage Examples

### Echo Bot v2 Workflow
1. Select a voice from the dropdown
2. Click "Start Recording" 
3. Speak your message (keep it under 30 seconds)
4. Click "Stop Recording"
5. Wait for processing (transcription + TTS)
6. Listen to your message in the selected AI voice!

---

**🎙️ Enjoy your Echo Bot v2 experience!** 

For issues or questions, check the API documentation at `http://127.0.0.1:8000/docs`

# Echo Bot v2 - TTS Echo with Murf AI

## Overview

Echo Bot v2 is an enhanced version that combines speech-to-text transcription with text-to-speech synthesis. Instead of just playing back your recorded audio, it:

1. Records your voice
2. Transcribes the audio using AssemblyAI
3. Generates new speech from the transcription using Murf AI voices
4. Plays back the AI-generated speech

## Features

- 🎙️ **Voice Recording**: Record your voice using your microphone
- 🎯 **Speech Recognition**: Transcribe speech using AssemblyAI
- 🎵 **Text-to-Speech**: Generate speech using Murf AI voices
- 🔄 **Voice Transformation**: Hear your words in different AI voices
- ⚡ **Real-time Processing**: Complete pipeline from voice to TTS audio

## New API Endpoint

### POST `/tts/echo`

Accepts audio file and returns TTS-generated audio URL.

**Parameters:**
- `audio_file` (file): Audio file to transcribe and convert to TTS
- `voice_id` (string): Murf voice ID (default: "en-US-sarah")
- `speed` (int): Speech speed 50-150% (default: 100)

**Response:**
```json
{
  "audio_url": "https://murf.ai/generated/audio/url.mp3",
  "status": "success",
  "message": "Echo TTS completed successfully",
  "transcription": "Your transcribed text here",
  "processing_time": 2.5
}
```

## Available Voices

- **Sarah (US)**: `en-US-sarah`
- **John (US)**: `en-US-john` 
- **Emma (UK)**: `en-GB-emma`

## How to Use

1. Start both servers:
   ```bash
   python start_servers.py
   ```

2. Open your browser and go to `http://127.0.0.1:5000`

3. Navigate to the "Echo Bot v2 - TTS Echo" section

4. Select your desired voice from the dropdown

5. Click "Start Recording" and speak into your microphone

6. Click "Stop Recording" when finished

7. Wait for the transcription and TTS generation to complete

8. The AI-generated speech will automatically play back

## Technical Implementation

The Echo Bot v2 uses a two-step pipeline:

1. **Transcription Step**: 
   - Audio is sent to AssemblyAI for speech-to-text conversion
   - High-quality transcription with punctuation and formatting

2. **TTS Generation Step**:
   - Transcribed text is sent to Murf AI for voice synthesis  
   - Professional AI voices with natural speech patterns
   - Customizable speed and voice selection

## Differences from Echo Bot v1

| Feature | Echo Bot v1 | Echo Bot v2 |
|---------|-------------|-------------|
| Audio Playback | ✅ Original recording | ✅ AI-generated speech |
| Voice Options | ❌ None | ✅ Multiple AI voices |
| Transcription | ❌ None | ✅ Full transcription shown |
| Customization | ❌ None | ✅ Voice and speed selection |
| Quality | 📱 Recording quality | 🎵 Professional AI voice |

## Error Handling

The system handles various error scenarios:

- **Microphone Access Denied**: Prompts user to grant permissions
- **Transcription Failures**: Shows detailed error messages
- **TTS Generation Errors**: Displays Murf API error details
- **Network Issues**: Timeout handling with user feedback

## API Keys Required

Make sure your `.env` file contains:

```env
ASSEMBLYAI_API_KEY=c32bee36fe5447ab8ea3d28044259d84
MURF_API_KEY=ap2_358dcb52-4f0c-43b6-a714-37c54fb80d9a
```

## Future Enhancements

Potential improvements for future versions:
- Real-time streaming transcription
- Voice cloning capabilities  
- Multiple language support
- Custom voice training
- Batch processing for multiple recordings

## Demo Instructions for LinkedIn

1. Record a short message (10-15 seconds)
2. Show the transcription appearing
3. Demonstrate different voice options
4. Play the AI-generated speech
5. Highlight the voice transformation effect
6. Mention the technology stack (AssemblyAI + Murf)
