# 30 Days of AI Voice Agents - Day 10: Chat History

## 🤖 Conversational AI Voice Agent with Memory

This is Day 10 of the 30 Days of AI Voice Agents challenge, implementing a **chat history feature** that allows the AI to remember previous messages in the conversation.

## 🌟 Features

### ✅ Day 10 New Features
- **Chat History Storage**: In-memory datastore for conversation history
- **Session Management**: Each conversation has a unique session ID
- **Context Awareness**: AI remembers previous messages for better responses
- **Conversation Continuity**: Natural conversational flow with memory
- **Session URL Parameters**: Share conversations via URL
- **Clear Chat History**: Start fresh conversations
- **Auto-Recording Hint**: Prompts user to continue conversation after AI response

### 🔄 Previous Features (Days 1-9)
- **Speech-to-Text**: Convert voice to text using AssemblyAI
- **LLM Processing**: Generate intelligent responses using Google Gemini
- **Text-to-Speech**: Convert AI responses to natural voice using Murf AI
- **Real-time Processing**: Complete voice-to-voice pipeline
- **Web Interface**: User-friendly chat interface
- **Multiple Voice Options**: Choose from various Murf AI voices

## 🏗️ Architecture

### Backend (FastAPI - Port 8000)
- **Chat History Management**: Store and retrieve conversation history
- **New Endpoint**: `POST /agent/chat/{session_id}` - Chat with history
- **History Endpoint**: `GET /agent/chat/{session_id}/history` - Get chat history
- **Clear Endpoint**: `DELETE /agent/chat/{session_id}` - Clear chat history
- **Context Formation**: Format chat history for LLM context
- **Memory Management**: Keep last 20 messages, use last 10 for context

### Frontend (Flask - Port 5000)
- **Chat Interface**: `/chat` - New conversational interface
- **Session Management**: URL-based session tracking
- **Hold-to-Record**: Intuitive recording interface
- **Real-time Chat**: Display conversation history
- **Auto-scroll**: Always show latest messages

### Data Flow
1. **User speaks** → Hold record button
2. **Audio captured** → WebM format
3. **STT Processing** → AssemblyAI transcription
4. **Context Building** → Combine with chat history
5. **LLM Processing** → Gemini generates contextual response
6. **History Storage** → Save user message + AI response
7. **TTS Generation** → Murf AI creates audio response
8. **Playback** → User hears AI response
9. **Continue Loop** → Ready for next message

## 🚀 Quick Start

### Option 1: Use Batch File (Windows)
```bash
double-click start_chat_bot.bat
```

### Option 2: Use Python Script
```bash
cd python-webapp
python run_chat_bot.py
```

### Option 3: Manual Start
```bash
# Terminal 1: Start FastAPI backend
cd python-webapp
python -m uvicorn fastapi_server:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start Flask frontend
cd python-webapp
python app.py
```

Then open: http://127.0.0.1:5000/chat

## 🎤 How to Use

1. **Start Conversation**: Hold the microphone button
2. **Speak Clearly**: Say your message while holding button
3. **Release Button**: Let go when finished speaking
4. **Wait for Processing**: AI transcribes, processes, and responds
5. **Listen to Response**: AI speaks back with context awareness
6. **Continue Chatting**: Hold button again for next message
7. **Clear History**: Use trash button to start fresh

## 🔧 Configuration

### API Keys Required
All API keys are configured in `.env` file:
- **MURF_API_KEY**: For text-to-speech generation
- **ASSEMBLYAI_API_KEY**: For speech-to-text transcription
- **GEMINI_API_KEY**: For LLM responses

### Chat History Settings
- **Max Messages**: 20 messages per session (configurable)
- **Context Window**: Last 10 messages sent to LLM
- **Storage**: In-memory (resets on server restart)
- **Session Duration**: Persistent until cleared or server restart

## 📊 New API Endpoints

### Chat with History
```http
POST /agent/chat/{session_id}
Content-Type: multipart/form-data

Form fields:
- audio_file: Audio file (WebM/MP3/WAV)
- voice_id: Murf voice ID (optional)
- speed: Speech speed 50-150% (optional)

Response:
{
  "response": "AI response text",
  "audio_url": "data:audio/mp3;base64,...",
  "status": "success",
  "message": "Chat agent query completed successfully",
  "transcription": "User's transcribed message",
  "session_id": "session_1234567890_abc123",
  "processing_time": 2.45
}
```

### Get Chat History
```http
GET /agent/chat/{session_id}/history

Response:
{
  "session_id": "session_1234567890_abc123",
  "chat_history": [
    {
      "role": "user",
      "content": "Hello, how are you?",
      "timestamp": "2024-01-15T10:30:00.123456"
    },
    {
      "role": "assistant", 
      "content": "Hello! I'm doing well, thank you for asking.",
      "timestamp": "2024-01-15T10:30:02.456789"
    }
  ],
  "status": "success",
  "message": "Retrieved 2 messages for session session_1234567890_abc123"
}
```

### Clear Chat History
```http
DELETE /agent/chat/{session_id}

Response:
{
  "status": "success",
  "message": "Chat history cleared for session session_1234567890_abc123"
}
```

## 🎯 Key Improvements Over Day 9

| Feature | Day 9 | Day 10 |
|---------|--------|--------|
| **Memory** | None | ✅ Remembers conversation |
| **Context** | Single message | ✅ Full conversation history |
| **Sessions** | Not supported | ✅ URL-based sessions |
| **Continuity** | Isolated responses | ✅ Contextual responses |
| **Interface** | Basic LLM audio | ✅ Chat-style interface |
| **Auto-recording** | Manual only | ✅ Hints after AI response |

## 🔄 Session Management

- **Session ID Format**: `session_TIMESTAMP_RANDOM`
- **URL Parameters**: `?session=session_id`
- **Persistence**: Until server restart or manual clear
- **Sharing**: Sessions can be shared via URL
- **Memory Limit**: Last 20 messages stored, last 10 used for context

## 🎭 Voice Options

Choose from multiple Murf AI voices:
- **Samantha (US)**: Professional female voice
- **Cooper (US)**: Professional male voice  
- **Hazel (UK)**: British female voice
- **Daniel (US)**: Casual male voice
- **Julia (US)**: Friendly female voice
- **Shane (AU)**: Australian male voice

## 🐛 Troubleshooting

### Common Issues
1. **Microphone Not Working**: Check browser permissions
2. **Audio Not Playing**: Check browser autoplay settings
3. **API Errors**: Verify API keys in `.env` file
4. **Session Lost**: Check if servers restarted
5. **Short Recording**: Record at least 1-2 seconds

### Browser Compatibility
- ✅ Chrome (recommended)
- ✅ Firefox  
- ✅ Edge
- ✅ Safari (with limitations)

## 📈 Performance Notes

- **Response Time**: ~2-5 seconds (depends on audio length)
- **Memory Usage**: ~1MB per session (20 messages)
- **Concurrency**: Supports multiple simultaneous sessions
- **Rate Limits**: Depends on API provider limits

## 🎯 Success Criteria

✅ **Complete working conversational bot by end of task**
✅ **Chat history stored in datastore**
✅ **Session-based conversations with memory**
✅ **LLM remembers previous messages**
✅ **UI stores session ID as URL parameter**
✅ **Auto-recording prompts after AI response**

## 🎬 Demo Video

Record a brief conversation with your bot showing:
1. Starting a new conversation
2. Multiple back-and-forth messages
3. AI remembering previous context
4. Clearing history and starting fresh

## 🔗 Links

- **Frontend**: http://127.0.0.1:5000/chat
- **Backend API**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

---

🎉 **Day 10 Complete!** You now have a fully functional conversational AI voice agent with memory and chat history!
