"""Chat and conversational agent Pydantic models."""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatHistoryEntry(BaseModel):
    """Single chat message entry."""
    role: str = Field(..., description="Role of the message sender", pattern="^(user|assistant)$")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO formatted timestamp")


class ChatHistoryResponse(BaseModel):
    """Response model for chat history retrieval."""
    session_id: str = Field(..., description="Chat session ID")
    chat_history: List[ChatHistoryEntry] = Field(..., description="List of chat messages")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human readable status message")


class ChatAgentResponse(BaseModel):
    """Response model for chat agent interaction."""
    response: str = Field(..., description="Agent generated response")
    audio_url: str = Field(..., description="URL or data URL of generated audio")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human readable status message")
    transcription: str = Field(..., description="Transcribed text from input audio")
    session_id: str = Field(..., description="Chat session ID")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds", ge=0.0)
