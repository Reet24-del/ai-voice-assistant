"""AssemblyAI transcription service."""

import io
import time
import tempfile
import os
from typing import Union
import assemblyai as aai
from fastapi import HTTPException, UploadFile

from config import settings
from utils import get_logger


class TranscriptionService:
    """Service for handling audio transcription using AssemblyAI."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self._configure_api()
    
    def _configure_api(self):
        """Configure AssemblyAI API with the API key."""
        if not settings.is_api_key_valid(settings.ASSEMBLYAI_API_KEY, "ASSEMBLYAI_API_KEY"):
            self.logger.error("AssemblyAI API key not configured properly")
            raise HTTPException(
                status_code=500,
                detail="ASSEMBLYAI_API_KEY not configured properly. Please add your real AssemblyAI API key to the .env file."
            )
        
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
        self.logger.info("AssemblyAI API configured successfully")
    
    async def transcribe_audio_file(self, audio_file: UploadFile) -> tuple[str, float, float]:
        """
        Transcribe an audio file.
        
        Args:
            audio_file: The audio file to transcribe
            
        Returns:
            Tuple of (transcription_text, confidence, processing_time)
        """
        start_time = time.time()
        
        try:
            # Validate file type
            if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Please upload an audio file."
                )
            
            # Read audio data
            audio_data = await audio_file.read()
            
            # Check if audio file is too small
            if len(audio_data) < settings.MIN_AUDIO_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Audio file is too small ({len(audio_data)} bytes). Please record at least 1-2 seconds of audio."
                )
            
            self.logger.info(f"Processing audio file: {audio_file.filename}, size: {len(audio_data)} bytes")
            
            # Transcribe using stream
            transcription_text = await self._transcribe_from_bytes(audio_data)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Transcription completed in {processing_time:.2f} seconds")
            
            return transcription_text, None, processing_time  # AssemblyAI doesn't provide confidence
            
        except HTTPException:
            raise
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Transcription error after {processing_time:.2f}s: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to transcribe audio: {str(e)}"
            )
    
    async def _transcribe_from_bytes(self, audio_data: bytes) -> str:
        """
        Transcribe audio from bytes data.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcription text
        """
        try:
            # Create a file-like object from audio data
            audio_stream = io.BytesIO(audio_data)
            
            # Create transcriber instance
            transcriber = aai.Transcriber()
            
            # Configure transcription settings
            config = aai.TranscriptionConfig(
                punctuate=True,
                format_text=True,
            )
            
            # Transcribe the audio
            transcript = transcriber.transcribe(audio_stream, config=config)
            
            # Check if transcription was successful
            if transcript.status == aai.TranscriptStatus.error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Transcription failed: {transcript.error}"
                )
            
            return transcript.text or "No speech detected in the audio file."
            
        except Exception as transcription_error:
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
    
    async def transcribe_with_temp_file(self, audio_data: bytes) -> str:
        """
        Transcribe audio by saving to temporary file (alternative method).
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcription text
        """
        temp_file_path = None
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Create transcriber instance
            transcriber = aai.Transcriber()
            
            # Configure transcription settings
            config = aai.TranscriptionConfig(
                punctuate=True,
                format_text=True,
            )
            
            # Transcribe from file
            transcript = transcriber.transcribe(temp_file_path, config=config)
            
            # Check if transcription was successful
            if transcript.status == aai.TranscriptStatus.error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Transcription failed: {transcript.error}"
                )
            
            return transcript.text or "No speech detected in the audio file."
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
