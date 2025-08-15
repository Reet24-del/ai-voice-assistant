from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import os
import time
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import assemblyai as aai
import io
import google.generativeai as genai
from datetime import datetime

# Load environment variables
load_dotenv()

# In-memory chat history datastore
# Key: session_id, Value: list of messages [{"role": "user", "content": "...", "timestamp": "..."}, ...]
chat_history_store: Dict[str, List[Dict[str, Any]]] = {}

app = FastAPI(title="TTS API", description="Text-to-Speech API using Murf", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "en-US-sarah"  # Default voice
    speed: int = 100  # Default speed (100 = normal)

class TTSResponse(BaseModel):
    audio_url: str
    status: str
    message: str

class AudioUploadResponse(BaseModel):
    filename: str
    content_type: str
    size: int
    status: str
    message: str

class TranscriptionResponse(BaseModel):
    transcription: str
    status: str
    message: str
    confidence: float = None
    processing_time: float = None

class EchoTTSResponse(BaseModel):
    audio_url: str
    status: str
    message: str
    transcription: str
    processing_time: float = None

class LLMQueryRequest(BaseModel):
    text: str

class LLMQueryResponse(BaseModel):
    response: str
    status: str
    message: str
    processing_time: float = None

class LLMAudioQueryResponse(BaseModel):
    response: str
    audio_url: str
    status: str
    message: str
    transcription: str
    processing_time: float = None

class ChatAgentResponse(BaseModel):
    response: str
    audio_url: str
    status: str
    message: str
    transcription: str
    session_id: str
    processing_time: float = None

class ChatHistoryEntry(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    session_id: str
    chat_history: List[ChatHistoryEntry]
    status: str
    message: str

@app.get("/")
async def root():
    return {"message": "TTS API Server is running"}

@app.post("/generate-tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    """
    Generate TTS audio using Murf's REST API
    """
    # Get API key from environment variables
    api_key = os.getenv("MURF_API_KEY")
    if not api_key or api_key == "your_actual_murf_api_key_here":
        raise HTTPException(
            status_code=500, 
            detail="MURF_API_KEY not configured properly. Please add your real Murf API key to the .env file. Use 'fastapi_server_mock.py' for testing without an API key."
        )
    
    # Murf API endpoint
    murf_url = "https://api.murf.ai/v1/speech/generate"
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prepare payload for Murf API
    payload = {
        "text": request.text,
        "voice_id": request.voice_id,
        "speed": request.speed,
        "format": "mp3"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(murf_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                # Assuming Murf returns an audio URL in the response
                audio_url = result.get("audio_url", "")
                
                return TTSResponse(
                    audio_url=audio_url,
                    status="success",
                    message="TTS generation completed successfully"
                )
            else:
                # Handle API errors
                error_detail = response.text if response.text else "Unknown error"
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Murf API error: {error_detail}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail="Request to Murf API timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/upload-audio", response_model=AudioUploadResponse)
async def upload_audio(audio_file: UploadFile = File(...)):
    """
    Upload an audio file to the server
    """
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        original_filename = audio_file.filename or "audio"
        name, ext = os.path.splitext(original_filename)
        
        # If no extension, try to determine from content type
        if not ext and audio_file.content_type:
            ext = mimetypes.guess_extension(audio_file.content_type) or ".webm"
        
        filename = f"{name}_{timestamp}{ext}"
        file_path = uploads_dir / filename
        
        # Read and save the file
        contents = await audio_file.read()
        file_size = len(contents)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return AudioUploadResponse(
            filename=filename,
            content_type=audio_file.content_type,
            size=file_size,
            status="success",
            message=f"Audio file uploaded successfully as {filename}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload audio file: {str(e)}"
        )

@app.post("/transcribe/file", response_model=TranscriptionResponse)
async def transcribe_audio_file(audio_file: UploadFile = File(...)):
    """
    Transcribe an audio file using AssemblyAI
    """
    start_time = time.time()
    
    try:
        # Get API key from environment variables
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key or api_key == "your_actual_assemblyai_api_key_here":
            raise HTTPException(
                status_code=500, 
                detail="ASSEMBLYAI_API_KEY not configured properly. Please add your real AssemblyAI API key to the .env file."
            )
        
        # Set the API key for AssemblyAI
        aai.settings.api_key = api_key
        
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Read the audio file content
        audio_data = await audio_file.read()
        
        # Create a file-like object from the audio data
        audio_stream = io.BytesIO(audio_data)
        
        # Create a transcriber instance
        transcriber = aai.Transcriber()
        
        # Configure transcription settings
        config = aai.TranscriptionConfig(
            # Enable additional features for better accuracy
            punctuate=True,
            format_text=True,
            # You can add more features here if needed
            # speaker_labels=True,  # Speaker identification
            # auto_highlights=True,  # Key phrase detection
        )
        
        # Transcribe the audio from the stream
        transcript = transcriber.transcribe(audio_stream, config=config)
        
        # Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcript.error}"
            )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Return the transcription result
        return TranscriptionResponse(
            transcription=transcript.text or "No speech detected in the audio file.",
            status="success",
            message="Audio transcribed successfully",
            confidence=transcript.confidence if hasattr(transcript, 'confidence') else None,
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Calculate processing time even for errors
        processing_time = time.time() - start_time
        
        # Log the error for debugging
        print(f"Transcription error: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

@app.post("/tts/echo", response_model=EchoTTSResponse)
async def tts_echo(audio_file: UploadFile = File(...), voice_id: str = Form("en-US-sarah"), speed: int = Form(100)):
    """
    Echo Bot with TTS: Transcribe audio and generate TTS response with Murf voice
    """
    start_time = time.time()
    
    try:
        # Get API keys from environment variables
        assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
        murf_key = os.getenv("MURF_API_KEY")
        
        if not assemblyai_key or assemblyai_key == "your_actual_assemblyai_api_key_here":
            raise HTTPException(
                status_code=500, 
                detail="ASSEMBLYAI_API_KEY not configured properly. Please add your real AssemblyAI API key to the .env file."
            )
        
        if not murf_key:
            raise HTTPException(
                status_code=500, 
                detail="MURF_API_KEY not configured properly. Please add your real Murf API key to the .env file."
            )
        
        # Set the API key for AssemblyAI
        aai.settings.api_key = assemblyai_key
        
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Step 1: Transcribe the audio using AssemblyAI
        audio_data = await audio_file.read()
        
        # Check if audio file is too small (likely invalid)
        if len(audio_data) < 1000:  # Less than 1KB
            raise HTTPException(
                status_code=400,
                detail="Audio file is too small or invalid. Please record at least 1-2 seconds of audio."
            )
        
        audio_stream = io.BytesIO(audio_data)
        
        # Create a transcriber instance
        transcriber = aai.Transcriber()
        
        # Configure transcription settings
        config = aai.TranscriptionConfig(
            punctuate=True,
            format_text=True,
        )
        
        try:
            # Transcribe the audio from the stream
            transcript = transcriber.transcribe(audio_stream, config=config)
        except Exception as transcription_error:
            # Handle transcription-specific errors
            error_msg = str(transcription_error)
            if "Upload failed" in error_msg:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid audio file format. Please use a supported audio format (WebM, MP3, WAV) and record at least 1-2 seconds of audio."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Transcription service error: {error_msg}"
                )
        
        # Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcript.error}"
            )
        
        transcribed_text = transcript.text or "No speech detected in the audio file."
        
        # Step 2: Generate TTS audio using Murf API
        murf_url = "https://api.murf.ai/v1/speech/generate"
        
        # Map voice IDs to actual Murf voices
        voice_mapping = {
            "en-US-sarah": "en-US-samantha",
            "en-US-john": "en-US-cooper", 
            "en-GB-emma": "en-UK-hazel",
            "en-US-david": "en-US-daniel",
            "en-US-jenny": "en-US-julia",
            "en-AU-william": "en-AU-shane"
        }
        
        murf_voice = voice_mapping.get(voice_id, "en-US-samantha")
        
        headers = {
            "api-key": murf_key,
            "Content-Type": "application/json"
        }
        
        # Convert speed percentage (50-150) to Murf rate (-50 to 50)
        # 50% = -50, 100% = 0, 150% = 50
        murf_rate = (speed - 100) // 2
        murf_rate = max(-50, min(50, murf_rate))  # Clamp to valid range
        
        payload = {
            "text": transcribed_text,
            "voiceId": murf_voice,
            "rate": murf_rate,
            "sampleRate": 48000,
            "format": "MP3",
            "channelType": "MONO"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(murf_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                # Murf returns audio data in base64 or audio URL
                audio_url = result.get("audioFile", result.get("url", ""))
                
                if not audio_url:
                    # If no direct URL, create a data URL from base64 audio data
                    audio_data = result.get("audioContent", "")
                    if audio_data:
                        audio_url = f"data:audio/mp3;base64,{audio_data}"
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                return EchoTTSResponse(
                    audio_url=audio_url,
                    status="success",
                    message="Echo TTS completed successfully",
                    transcription=transcribed_text,
                    processing_time=round(processing_time, 2)
                )
            else:
                # Handle Murf API errors
                error_detail = response.text if response.text else "Unknown error"
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Murf API error: {error_detail}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail="Request to Murf API timed out"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Calculate processing time even for errors
        processing_time = time.time() - start_time
        
        # Log the error for debugging
        print(f"Echo TTS error: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process echo TTS: {str(e)}"
        )

@app.post("/llm/query", response_model=LLMQueryResponse)
async def llm_query(request: LLMQueryRequest):
    """
    Query Google's Gemini LLM API to generate a response to the input text
    """
    start_time = time.time()
    
    try:
        # Get API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="GEMINI_API_KEY not configured. Please add your Gemini API key to the .env file."
            )
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model (using gemini-1.5-flash as it's available on the free tier)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response from the LLM
        response = model.generate_content(request.text)
        
        # Check if the response was successful
        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response from Gemini API. The response was empty."
            )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return LLMQueryResponse(
            response=response.text,
            status="success",
            message="LLM query completed successfully",
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Calculate processing time even for errors
        processing_time = time.time() - start_time
        
        # Log the error for debugging
        print(f"LLM query error: {str(e)}")
        
        # Handle specific Gemini API errors
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid API key" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid Gemini API key. Please check your API key configuration."
            )
        elif "QUOTA_EXCEEDED" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exceeded. Please try again later."
            )
        elif "PERMISSION_DENIED" in error_msg:
            raise HTTPException(
                status_code=403,
                detail="Permission denied. Please check your Gemini API key permissions."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process LLM query: {error_msg}"
            )

@app.post("/llm/query-audio", response_model=LLMAudioQueryResponse)
async def llm_query_audio(audio_file: UploadFile = File(...), voice_id: str = Form("en-US-sarah"), speed: int = Form(100)):
    """
    LLM Audio Query: Transcribe audio, send to LLM, and generate TTS response with Murf voice
    """
    start_time = time.time()
    
    try:
        # Get API keys from environment variables
        assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
        murf_key = os.getenv("MURF_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not assemblyai_key or assemblyai_key == "your_actual_assemblyai_api_key_here":
            raise HTTPException(
                status_code=500, 
                detail="ASSEMBLYAI_API_KEY not configured properly. Please add your real AssemblyAI API key to the .env file."
            )
        
        if not murf_key:
            raise HTTPException(
                status_code=500, 
                detail="MURF_API_KEY not configured properly. Please add your real Murf API key to the .env file."
            )
            
        if not gemini_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured. Please add your Gemini API key to the .env file."
            )
        
        # Set the API key for AssemblyAI
        aai.settings.api_key = assemblyai_key
        
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Step 1: Transcribe the audio using AssemblyAI
        audio_data = await audio_file.read()
        
        # Check if audio file is too small (likely invalid)
        if len(audio_data) < 1000:  # Less than 1KB
            raise HTTPException(
                status_code=400,
                detail="Audio file is too small or invalid. Please record at least 1-2 seconds of audio."
            )
        
        audio_stream = io.BytesIO(audio_data)
        
        # Create a transcriber instance
        transcriber = aai.Transcriber()
        
        # Configure transcription settings
        config = aai.TranscriptionConfig(
            punctuate=True,
            format_text=True,
        )
        
        try:
            # Transcribe the audio from the stream
            transcript = transcriber.transcribe(audio_stream, config=config)
        except Exception as transcription_error:
            # Handle transcription-specific errors
            error_msg = str(transcription_error)
            if "Upload failed" in error_msg:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid audio file format. Please use a supported audio format (WebM, MP3, WAV) and record at least 1-2 seconds of audio."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Transcription service error: {error_msg}"
                )
        
        # Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcript.error}"
            )
        
        transcribed_text = transcript.text or "No speech detected in the audio file."
        
        # Step 2: Send transcribed text to Gemini LLM
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response from the LLM
        llm_response = model.generate_content(transcribed_text)
        
        # Check if the LLM response was successful
        if not llm_response.text:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response from Gemini API. The response was empty."
            )
        
        llm_response_text = llm_response.text
        
        # Step 3: Generate TTS audio using Murf API
        murf_url = "https://api.murf.ai/v1/speech/generate"
        
        # Map voice IDs to actual Murf voices
        voice_mapping = {
            "en-US-sarah": "en-US-samantha",
            "en-US-john": "en-US-cooper", 
            "en-GB-emma": "en-UK-hazel",
            "en-US-david": "en-US-daniel",
            "en-US-jenny": "en-US-julia",
            "en-AU-william": "en-AU-shane"
        }
        
        murf_voice = voice_mapping.get(voice_id, "en-US-samantha")
        
        headers = {
            "api-key": murf_key,
            "Content-Type": "application/json"
        }
        
        # Convert speed percentage (50-150) to Murf rate (-50 to 50)
        # 50% = -50, 100% = 0, 150% = 50
        murf_rate = (speed - 100) // 2
        murf_rate = max(-50, min(50, murf_rate))  # Clamp to valid range
        
        payload = {
            "text": llm_response_text,
            "voiceId": murf_voice,
            "rate": murf_rate,
            "sampleRate": 48000,
            "format": "MP3",
            "channelType": "MONO"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(murf_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                # Murf returns audio data in base64 or audio URL
                audio_url = result.get("audioFile", result.get("url", ""))
                
                if not audio_url:
                    # If no direct URL, create a data URL from base64 audio data
                    audio_data = result.get("audioContent", "")
                    if audio_data:
                        audio_url = f"data:audio/mp3;base64,{audio_data}"
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                return LLMAudioQueryResponse(
                    response=llm_response_text,
                    audio_url=audio_url,
                    status="success",
                    message="LLM audio query completed successfully",
                    transcription=transcribed_text,
                    processing_time=round(processing_time, 2)
                )
            else:
                # Handle Murf API errors
                error_detail = response.text if response.text else "Unknown error"
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Murf API error: {error_detail}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail="Request to Murf API timed out"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Calculate processing time even for errors
        processing_time = time.time() - start_time
        
        # Log the error for debugging
        print(f"LLM audio query error: {str(e)}")
        
        # Handle specific Gemini API errors
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid API key" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid Gemini API key. Please check your API key configuration."
            )
        elif "QUOTA_EXCEEDED" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exceeded. Please try again later."
            )
        elif "PERMISSION_DENIED" in error_msg:
            raise HTTPException(
                status_code=403,
                detail="Permission denied. Please check your Gemini API key permissions."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process LLM audio query: {error_msg}"
            )

# Chat History Management Functions
def get_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """Get chat history for a session"""
    return chat_history_store.get(session_id, [])

def add_to_chat_history(session_id: str, role: str, content: str):
    """Add a message to chat history"""
    timestamp = datetime.now().isoformat()
    message = {
        "role": role,
        "content": content,
        "timestamp": timestamp
    }
    
    if session_id not in chat_history_store:
        chat_history_store[session_id] = []
    
    chat_history_store[session_id].append(message)
    
    # Keep only the last 20 messages to prevent memory issues
    if len(chat_history_store[session_id]) > 20:
        chat_history_store[session_id] = chat_history_store[session_id][-20:]

def format_chat_history_for_llm(chat_history: List[Dict[str, Any]]) -> str:
    """Format chat history for LLM context"""
    if not chat_history:
        return ""
    
    formatted_history = "Previous conversation:\n"
    for message in chat_history[-10:]:  # Use only last 10 messages for context
        role = "Human" if message["role"] == "user" else "Assistant"
        formatted_history += f"{role}: {message['content']}\n"
    
    formatted_history += "\nCurrent message:\n"
    return formatted_history

@app.post("/agent/chat/{session_id}", response_model=ChatAgentResponse)
async def chat_with_agent(session_id: str, audio_file: UploadFile = File(...), voice_id: str = Form("en-US-sarah"), speed: int = Form(100)):
    """
    Chat Agent with History: Transcribe audio, use chat history for context, send to LLM, store response, and generate TTS
    """
    start_time = time.time()
    
    try:
        # Get API keys from environment variables
        assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
        murf_key = os.getenv("MURF_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if not assemblyai_key or assemblyai_key == "your_actual_assemblyai_api_key_here":
            raise HTTPException(
                status_code=500, 
                detail="ASSEMBLYAI_API_KEY not configured properly. Please add your real AssemblyAI API key to the .env file."
            )
        
        if not murf_key:
            raise HTTPException(
                status_code=500, 
                detail="MURF_API_KEY not configured properly. Please add your real Murf API key to the .env file."
            )
            
        if not gemini_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured. Please add your Gemini API key to the .env file."
            )
        
        # Set the API key for AssemblyAI
        aai.settings.api_key = assemblyai_key
        
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Step 1: Transcribe the audio using AssemblyAI
        audio_data = await audio_file.read()
        
        # Check if audio file is too small (likely invalid)
        if len(audio_data) < 1000:  # Less than 1KB
            raise HTTPException(
                status_code=400,
                detail="Audio file is too small or invalid. Please record at least 1-2 seconds of audio."
            )
        
        # Save audio to temporary file for AssemblyAI
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Create a transcriber instance
            transcriber = aai.Transcriber()
            
            # Configure transcription settings
            config = aai.TranscriptionConfig(
                punctuate=True,
                format_text=True,
            )
            
            # Transcribe the audio from the temporary file
            transcript = transcriber.transcribe(temp_file_path, config=config)
        except Exception as transcription_error:
            # Handle transcription-specific errors
            error_msg = str(transcription_error)
            if "Upload failed" in error_msg:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid audio file format. Please use a supported audio format (WebM, MP3, WAV) and record at least 1-2 seconds of audio."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Transcription service error: {error_msg}"
                )
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        # Check if transcription was successful
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcript.error}"
            )
        
        transcribed_text = transcript.text or "No speech detected in the audio file."
        
        # Step 2: Get chat history and format for LLM context
        chat_history = get_chat_history(session_id)
        context = format_chat_history_for_llm(chat_history)
        
        # Combine context with current message
        llm_input = f"{context}Human: {transcribed_text}"
        
        # Step 3: Send to Gemini LLM with chat history context
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response from the LLM
        llm_response = model.generate_content(llm_input)
        
        # Check if the LLM response was successful
        if not llm_response.text:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response from Gemini API. The response was empty."
            )
        
        llm_response_text = llm_response.text
        
        # Step 4: Store both user message and assistant response in chat history
        add_to_chat_history(session_id, "user", transcribed_text)
        add_to_chat_history(session_id, "assistant", llm_response_text)
        
        # Step 5: Generate TTS audio using Murf API
        murf_url = "https://api.murf.ai/v1/speech/generate"
        
        # Map voice IDs to actual Murf voices
        voice_mapping = {
            "en-US-sarah": "en-US-samantha",
            "en-US-john": "en-US-cooper", 
            "en-GB-emma": "en-UK-hazel",
            "en-US-david": "en-US-daniel",
            "en-US-jenny": "en-US-julia",
            "en-AU-william": "en-AU-shane"
        }
        
        murf_voice = voice_mapping.get(voice_id, "en-US-samantha")
        
        headers = {
            "api-key": murf_key,
            "Content-Type": "application/json"
        }
        
        # Convert speed percentage (50-150) to Murf rate (-50 to 50)
        # 50% = -50, 100% = 0, 150% = 50
        murf_rate = (speed - 100) // 2
        murf_rate = max(-50, min(50, murf_rate))  # Clamp to valid range
        
        payload = {
            "text": llm_response_text,
            "voiceId": murf_voice,
            "rate": murf_rate,
            "sampleRate": 48000,
            "format": "MP3",
            "channelType": "MONO"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(murf_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                # Murf returns audio data in base64 or audio URL
                audio_url = result.get("audioFile", result.get("url", ""))
                
                if not audio_url:
                    # If no direct URL, create a data URL from base64 audio data
                    audio_data = result.get("audioContent", "")
                    if audio_data:
                        audio_url = f"data:audio/mp3;base64,{audio_data}"
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                return ChatAgentResponse(
                    response=llm_response_text,
                    audio_url=audio_url,
                    status="success",
                    message="Chat agent query completed successfully",
                    transcription=transcribed_text,
                    session_id=session_id,
                    processing_time=round(processing_time, 2)
                )
            else:
                # Handle Murf API errors
                error_detail = response.text if response.text else "Unknown error"
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Murf API error: {error_detail}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail="Request to Murf API timed out"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Calculate processing time even for errors
        processing_time = time.time() - start_time
        
        # Log the error for debugging
        print(f"Chat agent error: {str(e)}")
        
        # Handle specific Gemini API errors
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid API key" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid Gemini API key. Please check your API key configuration."
            )
        elif "QUOTA_EXCEEDED" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exceeded. Please try again later."
            )
        elif "PERMISSION_DENIED" in error_msg:
            raise HTTPException(
                status_code=403,
                detail="Permission denied. Please check your Gemini API key permissions."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process chat agent query: {error_msg}"
            )

@app.get("/agent/chat/{session_id}/history", response_model=ChatHistoryResponse)
async def get_session_chat_history(session_id: str):
    """
    Get chat history for a specific session
    """
    try:
        history = get_chat_history(session_id)
        
        # Convert to response format
        chat_entries = [
            ChatHistoryEntry(
                role=message["role"],
                content=message["content"],
                timestamp=message["timestamp"]
            )
            for message in history
        ]
        
        return ChatHistoryResponse(
            session_id=session_id,
            chat_history=chat_entries,
            status="success",
            message=f"Retrieved {len(chat_entries)} messages for session {session_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )

@app.delete("/agent/chat/{session_id}")
async def clear_session_chat_history(session_id: str):
    """
    Clear chat history for a specific session
    """
    try:
        if session_id in chat_history_store:
            del chat_history_store[session_id]
            return {"status": "success", "message": f"Chat history cleared for session {session_id}"}
        else:
            return {"status": "success", "message": f"No chat history found for session {session_id}"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat history: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TTS API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
