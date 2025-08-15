# 🎤 AI Voice Assistant - Advanced Conversational Platform

> A sophisticated multi-modal AI voice assistant that combines speech recognition, large language models, and text-to-speech synthesis to create natural conversational experiences.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.1-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Overview

This AI Voice Assistant is a comprehensive platform that enables natural voice interactions with AI. Built with modern web technologies and integrated with cutting-edge AI services, it offers multiple interaction modes from simple echo functionality to advanced conversational AI with memory.

### 🎯 Key Features

- **🎙️ Voice Recording & Playback** - High-quality audio capture and playback
- **🔊 Text-to-Speech (TTS)** - Powered by Murf AI with multiple voice options
- **📝 Speech-to-Text** - Accurate transcription using AssemblyAI
- **🤖 LLM Integration** - Google Gemini AI for intelligent responses
- **💬 Conversational Memory** - Context-aware chat with session management
- **🎨 Modern UI/UX** - Responsive Bootstrap interface with smooth animations
- **⚡ Real-time Processing** - Fast, asynchronous API responses
- **🔒 Robust Error Handling** - Comprehensive error management and fallbacks

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **FastAPI** - Modern async web framework for API server
- **Flask** - Lightweight web framework for frontend serving
- **Python 3.8+** - Core programming language
- **Uvicorn** - ASGI server for FastAPI

**AI/ML Services:**
- **AssemblyAI** - Speech-to-text transcription
- **Murf AI** - Text-to-speech synthesis
- **Google Gemini** - Large language model for conversations

**Frontend:**
- **HTML5** - Modern web standards with audio/media APIs
- **Bootstrap 5** - Responsive UI framework
- **Vanilla JavaScript** - No dependencies, pure JS implementation
- **Font Awesome** - Icon library

**Data Storage:**
- **In-Memory Store** - Session-based chat history management
- **File System** - Audio file uploads and temporary storage

## 📁 Project Structure

```
python-webapp/
├── 🐍 Core Application Files
│   ├── app.py                      # Flask frontend server
│   ├── fastapi_server.py           # Main FastAPI API server
│   ├── fastapi_server_robust.py    # Enhanced server with error handling
│   └── fastapi_server_mock.py      # Development server with mocked APIs
│
├── 🌐 Web Interface
│   ├── templates/
│   │   ├── index.html              # Main application interface
│   │   └── chat_bot.html           # Conversational chat interface
│   └── static/
│       ├── script.js               # Main JavaScript functionality
│       ├── script_robust.js        # Enhanced JS with error handling
│       └── style.css               # Custom CSS styles
│
├── 📁 Data & Configuration
│   ├── uploads/                    # Audio file storage
│   ├── static/                     # Fallback audio files
│   ├── .env                        # Environment variables (create from .env.example)
│   ├── .env.example                # Environment template
│   └── requirements.txt            # Python dependencies
│
├── 🧪 Testing & Development
│   ├── test_*.py                   # Various test scripts
│   ├── simulate_errors.py          # Error simulation for testing
│   ├── start_*.py                  # Server startup scripts
│   └── *.bat                       # Windows batch scripts
│
└── 📚 Documentation
    ├── README.md                   # This file
    ├── README_DAY10.md             # Day 10 specific documentation
    ├── README_ECHO_BOT_V2.md       # Echo bot documentation
    ├── README_ROBUST_ERROR_HANDLING.md  # Error handling guide
    ├── TTS_README.md               # TTS implementation guide
    └── llm_endpoint_examples.md    # LLM integration examples
```

## 🛠️ Setup & Installation

### Prerequisites

- **Python 3.8+** installed on your system
- **Git** for version control
- **Modern web browser** with microphone support
- **API Keys** for external services:
  - AssemblyAI API key
  - Murf AI API key (optional - mock server available)
  - Google Gemini API key

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd python-webapp
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env file with your API keys
   ```

### 🔐 Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required: AssemblyAI for speech-to-text
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# Required: Google Gemini for LLM responses
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional: Murf AI for text-to-speech (use mock server if not provided)
MURF_API_KEY=your_murf_api_key_here
```

**🔗 How to get API keys:**

- **AssemblyAI**: Sign up at [AssemblyAI](https://www.assemblyai.com/) → Dashboard → API Keys
- **Google Gemini**: Visit [Google AI Studio](https://makersuite.google.com/) → Get API Key
- **Murf AI**: Register at [Murf.ai](https://murf.ai/) → Account → API Access (optional)

## 🚀 Running the Application

### Method 1: Manual Server Start

**Terminal 1 - Start FastAPI server:**
```bash
python fastapi_server.py
```
*Server will run on: http://127.0.0.1:8000*

**Terminal 2 - Start Flask frontend:**
```bash
python app.py
```
*Frontend will run on: http://127.0.0.1:5000*

### Method 2: Automated Start (Windows)

```bash
# Start both servers automatically
start_servers.bat
```

### Method 3: Python Script

```bash
# Start both servers with Python
python start_servers.py
```

### 🧪 Development Mode

For development without API keys:
```bash
# Use mock server (no real APIs needed)
python fastapi_server_mock.py
```

## 📱 Application Features & Usage

### 🎙️ Main Interface (http://127.0.0.1:5000)

**Features available:**

1. **Text-to-Speech Generator**
   - Enter text and convert to speech
   - Multiple voice options (Samantha, Cooper, Hazel, etc.)
   - Adjustable speech speed (50-150%)

2. **Speech-to-Text Transcription**
   - Record voice and get instant transcription
   - High accuracy with AssemblyAI
   - Real-time feedback and status updates

3. **LLM Audio Assistant**
   - Ask questions with your voice
   - Get AI responses in text and speech
   - Powered by Google Gemini AI

4. **Echo Bot v2**
   - Record voice → transcribe → speak back
   - Perfect for testing voice pipeline

5. **Simple Echo Bot**
   - Basic record and playback functionality

### 💬 Conversational Chat (http://127.0.0.1:5000/chat)

**Advanced conversational AI features:**

- **Session Management**: Unique session IDs with URL persistence
- **Context Memory**: AI remembers conversation history
- **Hold-to-Record**: Intuitive voice input method
- **Real-time Feedback**: Visual recording and processing indicators
- **Multi-voice Support**: Choose from different AI voices
- **Chat History**: Full conversation log with timestamps
- **Clear/Reset**: Start fresh conversations anytime

## 🔌 API Endpoints

### Core FastAPI Endpoints (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API status check |
| `GET` | `/health` | Health check endpoint |
| `POST` | `/generate-tts` | Generate speech from text |
| `POST` | `/transcribe/file` | Transcribe audio file |
| `POST` | `/tts/echo` | Echo bot with TTS |
| `POST` | `/llm/query` | Query LLM with text |
| `POST` | `/llm/query-audio` | Query LLM with audio |
| `POST` | `/agent/chat/{session_id}` | Conversational chat |
| `GET` | `/agent/chat/{session_id}/history` | Get chat history |
| `DELETE` | `/agent/chat/{session_id}` | Clear chat history |
| `POST` | `/upload-audio` | Upload audio files |

### Flask Frontend Endpoints (Port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main application interface |
| `GET` | `/chat` | Conversational chat interface |
| `GET` | `/api/hello` | Simple API test endpoint |

## 🧪 Testing & Development

### Available Test Scripts

```bash
# Test basic functionality
python test_basic_functionality.py

# Test LLM integration
python test_llm_endpoint.py

# Test Murf TTS integration
python test_murf_integration.py

# Test transcription service
python test_transcription.py

# Test echo TTS functionality
python test_echo_tts.py

# Simulate various error conditions
python simulate_errors.py
```

### 🐛 Error Handling & Troubleshooting

**Common Issues:**

1. **Microphone Access Denied**
   - Ensure browser has microphone permissions
   - Check system privacy settings
   - Use HTTPS in production

2. **API Key Issues**
   - Verify all required API keys in `.env` file
   - Check API key validity and quotas
   - Use mock server for development

3. **Audio Format Issues**
   - Browser compatibility with WebM format
   - Fallback to different audio formats
   - Check file size limits

4. **Server Connection Issues**
   - Ensure both Flask and FastAPI servers are running
   - Check port availability (5000, 8000)
   - Verify CORS settings

## 🚀 Deployment

### Production Considerations

1. **Security**
   - Use HTTPS for production deployment
   - Implement proper API key management
   - Add rate limiting and authentication

2. **Performance**
   - Use production ASGI server (Gunicorn + Uvicorn)
   - Implement caching for frequently used responses
   - Optimize audio file handling

3. **Scalability**
   - Replace in-memory storage with persistent database
   - Implement session clustering
   - Use cloud storage for audio files

### Docker Deployment

```dockerfile
# Example Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "fastapi_server.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AssemblyAI** for excellent speech recognition APIs
- **Google** for the powerful Gemini AI model
- **Murf.ai** for high-quality text-to-speech synthesis
- **FastAPI** and **Flask** communities for amazing frameworks
- **Bootstrap** for responsive UI components

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the test scripts for examples
3. Open an issue on GitHub
4. Check existing documentation files

---

**Built with ❤️ using Python, FastAPI, Flask, and modern web technologies.**

*Happy coding! 🚀*
