"""TTS (Text-to-Speech) Pydantic models for request and response validation."""

from pydantic import BaseModel, Field
from typing import Optional


class TTSRequest(BaseModel):
    """Request model for TTS generation."""
    text: str = Field(..., description="Text to convert to speech", min_length=1)
    voice_id: str = Field(default="en-US-sarah", description="Voice ID for TTS")
    speed: int = Field(default=100, description="Speech speed percentage", ge=50, le=150)


class TTSResponse(BaseModel):
    """Response model for TTS generation."""
    audio_url: str = Field(..., description="URL or data URL of generated audio")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human readable status message")
