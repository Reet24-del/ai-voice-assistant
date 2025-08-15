"""Transcription and audio upload Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional


class AudioUploadResponse(BaseModel):
    """Response model for audio file upload."""
    filename: str = Field(..., description="Name of uploaded file")
    content_type: str = Field(..., description="MIME type of uploaded file")
    size: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human readable status message")


class TranscriptionResponse(BaseModel):
    """Response model for audio transcription."""
    transcription: str = Field(..., description="Transcribed text from audio")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human readable status message")
    confidence: Optional[float] = Field(None, description="Confidence score", ge=0.0, le=1.0)
    processing_time: Optional[float] = Field(None, description="Processing time in seconds", ge=0.0)
