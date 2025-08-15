from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
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
import logging
import json
import base64
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# In-memory chat history datastore
# Key: session_id, Value: list of messages [{"role": "user", "content": "...", "timestamp": "..."}, ...]
chat_history_store: Dict[str, List[Dict[str, Any]]] = {}

app = FastAPI(title="Robust TTS API", description="Robust Text-to-Speech API with comprehensive error handling", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error response models
class ErrorResponse(BaseModel):
    error: str
    message: str
    fallback_audio_url: Optional[str] = None
    timestamp: str

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "en-US-sarah"  # Default voice
    speed: int = 100  # Default speed (100 = normal)

class TTSResponse(BaseModel):
    audio_url: str
    status: str
    message: str
    fallback_used: bool = False

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
    fallback_used: bool = False

class EchoTTSResponse(BaseModel):
    audio_url: str
    status: str
    message: str
    transcription: str
    processing_time: float = None
    fallback_used: bool = False

class LLMQueryRequest(BaseModel):
    text: str

class LLMQueryResponse(BaseModel):
    response: str
    status: str
    message: str
    processing_time: float = None
    fallback_used: bool = False

class LLMAudioQueryResponse(BaseModel):
    response: str
    audio_url: str
    status: str
    message: str
    transcription: str
    processing_time: float = None
    fallback_used: bool = False

class ChatAgentResponse(BaseModel):
    response: str
    audio_url: str
    status: str
    message: str
    transcription: str
    session_id: str
    processing_time: float = None
    fallback_used: bool = False

class ChatHistoryEntry(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    session_id: str
    chat_history: List[ChatHistoryEntry]
    status: str
    message: str

# Mount static files for serving fallback audio
app.mount("/static", StaticFiles(directory="static"), name="static")

# Utility functions for error handling
def get_fallback_audio_url(fallback_type: str = "connection_issue") -> str:
    """
    Get the URL for a fallback audio file
    """
    fallback_files = {
        "connection_issue": "fallback_connection_issue.wav",
        "service_unavailable": "fallback_service_unavailable.wav", 
        "general_error": "fallback_general_error.wav",
        "transcription_failed": "fallback_transcription_failed.wav",
        "llm_unavailable": "fallback_llm_unavailable.wav"
    }
    
    filename = fallback_files.get(fallback_type, fallback_files["connection_issue"])
    static_path = Path("static") / filename
    
    # Check if the file exists
    if static_path.exists():
        return f"http://127.0.0.1:8000/static/{filename}"
    else:
        logger.warning(f"Fallback audio file not found: {static_path}")
        # Return a data URL as ultimate fallback
        silent_audio = "UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2+LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmAaAziF0e/NfSwEJXfH8N2QQAoUXrTp66hVFApGn+DyvmAaAziF0e/NfSwE"
        return f"data:audio/wav;base64,{silent_audio}"

def get_fallback_llm_response(user_input: str) -> str:
    """
    Generate a fallback response when LLM APIs fail
    """
    fallback_responses = [
        "I'm experiencing some technical difficulties right now. Please try asking your question again in a moment.",
        "I'm having trouble processing your request at the moment. Could you please rephrase your question?",
        "My AI services are temporarily unavailable. Please check back in a few minutes.",
        "I'm currently unable to connect to my knowledge base. Please try again shortly.",
        "There seems to be a connection issue on my end. Please give me a moment and try again."
    ]
    
    # Simple keyword-based fallback for common queries
    user_lower = user_input.lower()
    if any(word in user_lower for word in ["hello", "hi", "hey"]):
        return "Hello! I'm having some technical issues right now, but I'm glad you reached out. Please try again in a moment."
    elif any(word in user_lower for word in ["help", "support"]):
        return "I'd love to help, but I'm experiencing some connectivity issues at the moment. Please try your request again shortly."
    elif any(word in user_lower for word in ["weather", "time", "date"]):
        return "I'm unable to access current information right now due to technical difficulties. Please try again in a few minutes."
    else:
        import random
        return random.choice(fallback_responses)

def validate_api_keys() -> Dict[str, bool]:
    """
    Validate all API keys and return their status
    """
    api_status = {
        'murf': False,
        'assemblyai': False,
        'gemini': False
    }
    
    try:
        murf_key = os.getenv("MURF_API_KEY")
        if murf_key and murf_key != "your_actual_murf_api_key_here" and len(murf_key) > 10:
            api_status['murf'] = True
    except Exception:
        pass
    
    try:
        assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
        if assemblyai_key and assemblyai_key != "your_actual_assemblyai_api_key_here" and len(assemblyai_key) > 10:
            api_status['assemblyai'] = True
    except Exception:
        pass
    
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and len(gemini_key) > 10:
            api_status['gemini'] = True
    except Exception:
        pass
    
    return api_status

@app.get("/")
async def root():
    return {"message": "Robust TTS API Server is running", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Enhanced health check with API status"""
    api_status = validate_api_keys()
    return {
        "status": "healthy", 
        "service": "Robust TTS API",
        "version": "2.0.0",
        "api_keys": api_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/generate-tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    """
    Generate TTS audio using Murf's REST API with comprehensive error handling
    """
    start_time = time.time()
    logger.info(f"TTS request received: text='{request.text[:50]}...', voice={request.voice_id}")
    
    try:
        # Get API key from environment variables
        api_key = os.getenv("MURF_API_KEY")
        if not api_key or api_key == "your_actual_murf_api_key_here":
            logger.warning("MURF_API_KEY not configured, using fallback")
            fallback_audio = get_fallback_audio_url("service_unavailable")
            return TTSResponse(
                audio_url=fallback_audio,
                status="success",
                message="Using fallback audio due to API configuration issue",
                fallback_used=True
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
        
        # Try Murf API with timeout and retries
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(2):  # Try twice
                try:
                    logger.info(f"Calling Murf API (attempt {attempt + 1})")
                    response = await client.post(murf_url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        audio_url = result.get("audio_url", "")
                        
                        if audio_url:
                            logger.info("TTS generation successful")
                            return TTSResponse(
                                audio_url=audio_url,
                                status="success",
                                message="TTS generation completed successfully"
                            )
                        else:
                            logger.warning("No audio URL in Murf response")
                            break
                    
                    elif response.status_code in [429, 503]:  # Rate limit or service unavailable
                        if attempt == 0:
                            await asyncio.sleep(2)  # Wait before retry
                            continue
                        else:
                            break
                    else:
                        logger.error(f"Murf API error: {response.status_code} - {response.text}")
                        break
                        
                except httpx.TimeoutException:
                    logger.warning(f"Murf API timeout on attempt {attempt + 1}")
                    if attempt == 0:
                        continue
                    else:
                        break
                except Exception as e:
                    logger.error(f"Murf API request error on attempt {attempt + 1}: {str(e)}")
                    break
        
        # If we reach here, Murf API failed - use fallback
        logger.warning("Murf API failed, using fallback audio")
        fallback_audio = get_fallback_audio_url("connection_issue")
        return TTSResponse(
            audio_url=fallback_audio,
            status="success",
            message="Using fallback audio due to TTS service unavailability",
            fallback_used=True
        )
                
    except Exception as e:
        logger.error(f"TTS generation error: {str(e)}")
        fallback_audio = get_fallback_audio_url("general_error")
        return TTSResponse(
            audio_url=fallback_audio,
            status="success",
            message="Using fallback audio due to unexpected error",
            fallback_used=True
        )

@app.post("/transcribe/file", response_model=TranscriptionResponse)
async def transcribe_audio_file(audio_file: UploadFile = File(...)):
    """
    Transcribe an audio file using AssemblyAI with comprehensive error handling
    """
    start_time = time.time()
    logger.info(f"Transcription request received: file={audio_file.filename}")
    
    try:
        # Get API key from environment variables
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key or api_key == "your_actual_assemblyai_api_key_here":
            logger.warning("ASSEMBLYAI_API_KEY not configured, using fallback")
            return TranscriptionResponse(
                transcription="Speech-to-text service is temporarily unavailable. Please try again later.",
                status="success",
                message="Using fallback transcription due to API configuration issue",
                processing_time=round(time.time() - start_time, 2),
                fallback_used=True
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
        
        if len(audio_data) < 100:  # Very small file
            return TranscriptionResponse(
                transcription="Audio file too small or invalid. Please record at least 2 seconds of speech.",
                status="success",
                message="Fallback message for invalid audio",
                processing_time=round(time.time() - start_time, 2),
                fallback_used=True
            )
        
        # Create a file-like object from the audio data
        audio_stream = io.BytesIO(audio_data)
        
        try:
            # Create a transcriber instance
            transcriber = aai.Transcriber()
            
            # Configure transcription settings
            config = aai.TranscriptionConfig(
                punctuate=True,
                format_text=True,
            )
            
            logger.info("Calling AssemblyAI transcription service")
            # Transcribe the audio from the stream
            transcript = transcriber.transcribe(audio_stream, config=config)
            
            # Check if transcription was successful
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"AssemblyAI transcription failed: {transcript.error}")
                raise Exception(f"Transcription failed: {transcript.error}")
            
            transcription_text = transcript.text or "No speech detected in the audio file."
            
            # Calculate processing time
            processing_time = time.time() - start_time
            logger.info("Transcription successful")
            
            return TranscriptionResponse(
                transcription=transcription_text,
                status="success",
                message="Audio transcribed successfully",
                confidence=transcript.confidence if hasattr(transcript, 'confidence') else None,
                processing_time=round(processing_time, 2)
            )
            
        except Exception as transcription_error:
            logger.error(f"AssemblyAI transcription error: {str(transcription_error)}")
            
            # Return fallback response
            processing_time = time.time() - start_time
            return TranscriptionResponse(
                transcription="I'm having trouble understanding the audio right now. Please try speaking more clearly or check your microphone.",
                status="success",
                message="Using fallback transcription due to service error",
                processing_time=round(processing_time, 2),
                fallback_used=True
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Transcription endpoint error: {str(e)}")
        
        # Calculate processing time even for errors
        processing_time = time.time() - start_time
        
        return TranscriptionResponse(
            transcription="Speech recognition service is experiencing difficulties. Please try again.",
            status="success",
            message="Using fallback transcription due to unexpected error",
            processing_time=round(processing_time, 2),
            fallback_used=True
        )

@app.post("/llm/query", response_model=LLMQueryResponse)
async def llm_query(request: LLMQueryRequest):
    """
    Query Google's Gemini LLM API with comprehensive error handling
    """
    start_time = time.time()
    logger.info(f"LLM query received: text='{request.text[:50]}...'")
    
    try:
        # Get API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            logger.warning("GEMINI_API_KEY not configured, using fallback")
            fallback_response = get_fallback_llm_response(request.text)
            return LLMQueryResponse(
                response=fallback_response,
                status="success",
                message="Using fallback response due to API configuration issue",
                processing_time=round(time.time() - start_time, 2),
                fallback_used=True
            )
        
        try:
            # Configure the Gemini API
            genai.configure(api_key=api_key)
            
            # Initialize the model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            logger.info("Calling Gemini API")
            # Generate response from the LLM
            response = model.generate_content(request.text)
            
            # Check if the response was successful
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            logger.info("LLM query successful")
            
            return LLMQueryResponse(
                response=response.text,
                status="success",
                message="LLM query completed successfully",
                processing_time=round(processing_time, 2)
            )
            
        except Exception as llm_error:
            logger.error(f"Gemini API error: {str(llm_error)}")
            
            # Handle specific Gemini API errors and provide fallback
            error_msg = str(llm_error).lower()
            
            if any(keyword in error_msg for keyword in ["api_key_invalid", "invalid api key", "unauthorized"]):
                fallback_msg = "I'm having authentication issues right now. Please try again in a moment."
            elif any(keyword in error_msg for keyword in ["quota_exceeded", "quota", "limit"]):
                fallback_msg = "I'm currently at my usage limit. Please try again in a few minutes."
            elif any(keyword in error_msg for keyword in ["permission_denied", "forbidden"]):
                fallback_msg = "I don't have permission to process that request right now. Please try again later."
            else:
                fallback_msg = get_fallback_llm_response(request.text)
            
            processing_time = time.time() - start_time
            return LLMQueryResponse(
                response=fallback_msg,
                status="success",
                message="Using fallback response due to LLM service error",
                processing_time=round(processing_time, 2),
                fallback_used=True
            )
        
    except Exception as e:
        logger.error(f"LLM query endpoint error: {str(e)}")
        
        # Calculate processing time even for errors
        processing_time = time.time() - start_time
        
        fallback_response = get_fallback_llm_response(request.text)
        return LLMQueryResponse(
            response=fallback_response,
            status="success",
            message="Using fallback response due to unexpected error",
            processing_time=round(processing_time, 2),
            fallback_used=True
        )

# Additional comprehensive endpoints with error handling...
@app.post("/llm/query-audio", response_model=LLMAudioQueryResponse)
async def llm_query_audio(audio_file: UploadFile = File(...), voice_id: str = Form("en-US-sarah"), speed: int = Form(100)):
    """
    LLM Audio Query: Transcribe audio, send to LLM, and generate TTS response with comprehensive error handling
    """
    start_time = time.time()
    logger.info(f"LLM audio query received: file={audio_file.filename}")
    
    fallback_audio = get_fallback_audio_url("llm_unavailable")
    fallback_transcription = "I couldn't understand the audio clearly."
    fallback_response = "I'm having technical difficulties processing your voice message right now."
    
    try:
        # Step 1: Transcribe audio (with fallback)
        transcription_result = await transcribe_audio_file(audio_file)
        transcription = transcription_result.transcription
        
        # Step 2: Get LLM response (with fallback)
        llm_request = LLMQueryRequest(text=transcription)
        llm_result = await llm_query(llm_request)
        llm_response_text = llm_result.response
        
        # Step 3: Generate TTS (with fallback)
        tts_request = TTSRequest(text=llm_response_text, voice_id=voice_id, speed=speed)
        tts_result = await generate_tts(tts_request)
        audio_url = tts_result.audio_url
        
        # Check if any fallbacks were used
        fallback_used = (transcription_result.fallback_used or 
                        llm_result.fallback_used or 
                        tts_result.fallback_used)
        
        processing_time = time.time() - start_time
        logger.info(f"LLM audio query completed (fallback_used={fallback_used})")
        
        return LLMAudioQueryResponse(
            response=llm_response_text,
            audio_url=audio_url,
            status="success",
            message="LLM audio query completed" + (" with fallbacks" if fallback_used else " successfully"),
            transcription=transcription,
            processing_time=round(processing_time, 2),
            fallback_used=fallback_used
        )
        
    except Exception as e:
        logger.error(f"LLM audio query error: {str(e)}")
        processing_time = time.time() - start_time
        
        return LLMAudioQueryResponse(
            response=fallback_response,
            audio_url=fallback_audio,
            status="success",
            message="Using complete fallback due to service error",
            transcription=fallback_transcription,
            processing_time=round(processing_time, 2),
            fallback_used=True
        )

# Chat history management functions (unchanged but with logging)
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
    
    logger.info(f"Added message to chat history for session {session_id}")

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

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Robust TTS API server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
