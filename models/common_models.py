"""Common models used across different functionalities."""

from pydantic import BaseModel, Field
from typing import Optional


class EchoTTSResponse(BaseModel):
    """Response model for echo TTS functionality (transcribe -> TTS back)."""
    audio_url: str = Field(..., description="URL or data URL of generated audio")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human readable status message")
    transcription: str = Field(..., description="Transcribed text from input audio")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds", ge=0.0)
