"""LLM (Large Language Model) Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional


class LLMQueryRequest(BaseModel):
    """Request model for LLM text query."""
    text: str = Field(..., description="Text to send to LLM", min_length=1)


class LLMQueryResponse(BaseModel):
    """Response model for LLM text query."""
    response: str = Field(..., description="LLM generated response")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human readable status message")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds", ge=0.0)


class LLMAudioQueryResponse(BaseModel):
    """Response model for LLM audio query (transcribe -> LLM -> TTS)."""
    response: str = Field(..., description="LLM generated response")
    audio_url: str = Field(..., description="URL or data URL of generated audio")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human readable status message")
    transcription: str = Field(..., description="Transcribed text from input audio")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds", ge=0.0)
