"""
AI Voice Assistant - Refactored FastAPI Server

A sophisticated multi-modal AI voice assistant that combines speech recognition,
large language models, and text-to-speech synthesis.
"""

import time
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
import mimetypes

from config import settings
from utils import get_logger
from models import (
    TTSRequest, TTSResponse, TranscriptionResponse, AudioUploadResponse,
    LLMQueryRequest, LLMQueryResponse, LLMAudioQueryResponse,
    ChatAgentResponse, ChatHistoryResponse, ChatHistoryEntry,
    EchoTTSResponse
)
from services import TranscriptionService, TTSService, LLMService, ChatService


# Initialize logger
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice Assistant API",
    description="Advanced conversational platform combining STT, LLM, and TTS",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances (dependency injection)
transcription_service = TranscriptionService()
tts_service = TTSService()
llm_service = LLMService()
chat_service = ChatService()


def get_transcription_service() -> TranscriptionService:
    """Dependency injection for transcription service."""
    return transcription_service


def get_tts_service() -> TTSService:
    """Dependency injection for TTS service.""" 
    return tts_service


def get_llm_service() -> LLMService:
    """Dependency injection for LLM service."""
    return llm_service


def get_chat_service() -> ChatService:
    """Dependency injection for chat service."""
    return chat_service


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting AI Voice Assistant API server...")
    
    # Validate required API keys
    missing_keys = settings.validate_required_keys()
    if missing_keys:
        logger.warning(f"Missing required API keys: {', '.join(missing_keys)}")
        logger.warning("Some endpoints may not function properly without proper API keys")
    else:
        logger.info("All required API keys are configured")
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    logger.info(f"Upload directory ready: {upload_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down AI Voice Assistant API server...")


@app.get("/")
async def root():
    """API status check endpoint."""
    return {
        "message": "AI Voice Assistant API Server is running",
        "version": "2.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "AI Voice Assistant API",
        "version": "2.0.0"
    }


@app.post("/generate-tts", response_model=TTSResponse)
async def generate_tts(
    request: TTSRequest,
    tts_svc: TTSService = Depends(get_tts_service)
):
    """Generate TTS audio using Murf's REST API."""
    logger.info(f"TTS request: text_length={len(request.text)}, voice={request.voice_id}, speed={request.speed}")
    
    try:
        audio_url = await tts_svc.generate_speech(
            text=request.text,
            voice_id=request.voice_id,
            speed=request.speed
        )
        
        return TTSResponse(
            audio_url=audio_url,
            status="success",
            message="TTS generation completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/upload-audio", response_model=AudioUploadResponse)
async def upload_audio(audio_file: UploadFile = File(...)):
    """Upload an audio file to the server."""
    logger.info(f"Audio upload request: filename={audio_file.filename}, content_type={audio_file.content_type}")
    
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path(settings.UPLOAD_DIR)
        uploads_dir.mkdir(exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = int(time.time() * 1000)
        original_filename = audio_file.filename or "audio"
        name, ext = os.path.splitext(original_filename)
        
        # Determine extension from content type if missing
        if not ext and audio_file.content_type:
            ext = mimetypes.guess_extension(audio_file.content_type) or ".webm"
        
        filename = f"{name}_{timestamp}{ext}"
        file_path = uploads_dir / filename
        
        # Read and save the file
        contents = await audio_file.read()
        file_size = len(contents)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"Audio file uploaded: {filename} ({file_size} bytes)")
        
        return AudioUploadResponse(
            filename=filename,
            content_type=audio_file.content_type,
            size=file_size,
            status="success",
            message=f"Audio file uploaded successfully as {filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio upload failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload audio file: {str(e)}"
        )


@app.post("/transcribe/file", response_model=TranscriptionResponse)
async def transcribe_audio_file(
    audio_file: UploadFile = File(...),
    transcription_svc: TranscriptionService = Depends(get_transcription_service)
):
    """Transcribe an audio file using AssemblyAI."""
    logger.info(f"Transcription request: filename={audio_file.filename}")
    
    try:
        transcription, confidence, processing_time = await transcription_svc.transcribe_audio_file(audio_file)
        
        logger.info(f"Transcription completed in {processing_time:.2f}s")
        
        return TranscriptionResponse(
            transcription=transcription,
            status="success",
            message="Audio transcribed successfully",
            confidence=confidence,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )


@app.post("/tts/echo", response_model=EchoTTSResponse)
async def tts_echo(
    audio_file: UploadFile = File(...),
    voice_id: str = Form("en-US-sarah"),
    speed: int = Form(100),
    transcription_svc: TranscriptionService = Depends(get_transcription_service),
    tts_svc: TTSService = Depends(get_tts_service)
):
    """Echo Bot with TTS: Transcribe audio and generate TTS response."""
    start_time = time.time()
    logger.info(f"Echo TTS request: filename={audio_file.filename}, voice={voice_id}, speed={speed}")
    
    try:
        # Step 1: Transcribe the audio
        transcription, _, _ = await transcription_svc.transcribe_audio_file(audio_file)
        
        # Step 2: Generate TTS from transcription
        audio_url = await tts_svc.generate_speech(
            text=transcription,
            voice_id=voice_id,
            speed=speed
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Echo TTS completed in {processing_time:.2f}s")
        
        return EchoTTSResponse(
            audio_url=audio_url,
            status="success",
            message="Echo TTS completed successfully",
            transcription=transcription,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Echo TTS failed after {processing_time:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process echo TTS: {str(e)}"
        )


@app.post("/llm/query", response_model=LLMQueryResponse)
async def llm_query(
    request: LLMQueryRequest,
    llm_svc: LLMService = Depends(get_llm_service)
):
    """Query Google's Gemini LLM API to generate a response."""
    start_time = time.time()
    logger.info(f"LLM query request: text_length={len(request.text)}")
    
    try:
        response_text = await llm_svc.generate_response(request.text)
        
        processing_time = time.time() - start_time
        logger.info(f"LLM query completed in {processing_time:.2f}s")
        
        return LLMQueryResponse(
            response=response_text,
            status="success",
            message="LLM query completed successfully",
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"LLM query failed after {processing_time:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process LLM query: {str(e)}"
        )


@app.post("/llm/query-audio", response_model=LLMAudioQueryResponse)
async def llm_query_audio(
    audio_file: UploadFile = File(...),
    voice_id: str = Form("en-US-sarah"),
    speed: int = Form(100),
    transcription_svc: TranscriptionService = Depends(get_transcription_service),
    llm_svc: LLMService = Depends(get_llm_service),
    tts_svc: TTSService = Depends(get_tts_service)
):
    """LLM Audio Query: Transcribe audio, send to LLM, and generate TTS response."""
    start_time = time.time()
    logger.info(f"LLM audio query request: filename={audio_file.filename}, voice={voice_id}, speed={speed}")
    
    try:
        # Step 1: Transcribe the audio
        transcription, _, _ = await transcription_svc.transcribe_audio_file(audio_file)
        
        # Step 2: Send transcribed text to LLM
        llm_response = await llm_svc.generate_response(transcription)
        
        # Step 3: Generate TTS from LLM response
        audio_url = await tts_svc.generate_speech(
            text=llm_response,
            voice_id=voice_id,
            speed=speed
        )
        
        processing_time = time.time() - start_time
        logger.info(f"LLM audio query completed in {processing_time:.2f}s")
        
        return LLMAudioQueryResponse(
            response=llm_response,
            audio_url=audio_url,
            status="success",
            message="LLM audio query completed successfully",
            transcription=transcription,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"LLM audio query failed after {processing_time:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process LLM audio query: {str(e)}"
        )


@app.post("/agent/chat/{session_id}", response_model=ChatAgentResponse)
async def chat_with_agent(
    session_id: str,
    audio_file: UploadFile = File(...),
    voice_id: str = Form("en-US-sarah"),
    speed: int = Form(100),
    transcription_svc: TranscriptionService = Depends(get_transcription_service),
    llm_svc: LLMService = Depends(get_llm_service),
    tts_svc: TTSService = Depends(get_tts_service),
    chat_svc: ChatService = Depends(get_chat_service)
):
    """Chat Agent with History: Conversational AI with context memory."""
    start_time = time.time()
    logger.info(f"Chat agent request: session={session_id}, filename={audio_file.filename}, voice={voice_id}, speed={speed}")
    
    try:
        # Step 1: Transcribe the audio
        transcription, _, _ = await transcription_svc.transcribe_audio_file(audio_file)
        
        # Step 2: Get chat history and format for LLM context
        chat_history = chat_svc.get_chat_history(session_id)
        context = chat_svc.format_chat_history_for_llm(chat_history)
        
        # Step 3: Generate LLM response with context
        llm_response = await llm_svc.generate_with_context(transcription, context)
        
        # Step 4: Store chat history
        chat_svc.add_to_chat_history(session_id, "user", transcription)
        chat_svc.add_to_chat_history(session_id, "assistant", llm_response)
        
        # Step 5: Generate TTS from LLM response
        audio_url = await tts_svc.generate_speech(
            text=llm_response,
            voice_id=voice_id,
            speed=speed
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Chat agent interaction completed in {processing_time:.2f}s")
        
        return ChatAgentResponse(
            response=llm_response,
            audio_url=audio_url,
            status="success",
            message="Chat agent query completed successfully",
            transcription=transcription,
            session_id=session_id,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Chat agent failed after {processing_time:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat agent query: {str(e)}"
        )


@app.get("/agent/chat/{session_id}/history", response_model=ChatHistoryResponse)
async def get_session_chat_history(
    session_id: str,
    chat_svc: ChatService = Depends(get_chat_service)
):
    """Get chat history for a specific session."""
    logger.info(f"Chat history request: session={session_id}")
    
    try:
        history = chat_svc.get_chat_history(session_id)
        
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
        logger.error(f"Failed to retrieve chat history for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


@app.delete("/agent/chat/{session_id}")
async def clear_session_chat_history(
    session_id: str,
    chat_svc: ChatService = Depends(get_chat_service)
):
    """Clear chat history for a specific session."""
    logger.info(f"Clear chat history request: session={session_id}")
    
    try:
        existed = chat_svc.clear_chat_history(session_id)
        
        if existed:
            return {"status": "success", "message": f"Chat history cleared for session {session_id}"}
        else:
            return {"status": "success", "message": f"No chat history found for session {session_id}"}
        
    except Exception as e:
        logger.error(f"Failed to clear chat history for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat history: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
