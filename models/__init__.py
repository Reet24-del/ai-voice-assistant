# Models package - Pydantic models for request/response validation

from .tts_models import TTSRequest, TTSResponse
from .transcription_models import TranscriptionResponse, AudioUploadResponse
from .llm_models import LLMQueryRequest, LLMQueryResponse, LLMAudioQueryResponse
from .chat_models import (
    ChatAgentResponse, 
    ChatHistoryEntry, 
    ChatHistoryResponse
)
from .common_models import EchoTTSResponse

__all__ = [
    # TTS Models
    "TTSRequest",
    "TTSResponse",
    
    # Transcription Models
    "TranscriptionResponse",
    "AudioUploadResponse",
    
    # LLM Models
    "LLMQueryRequest",
    "LLMQueryResponse", 
    "LLMAudioQueryResponse",
    
    # Chat Models
    "ChatAgentResponse",
    "ChatHistoryEntry",
    "ChatHistoryResponse",
    
    # Common Models
    "EchoTTSResponse"
]
