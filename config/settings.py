"""Application configuration settings."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings configuration."""

    # API Keys
    ASSEMBLYAI_API_KEY: str = os.getenv("ASSEMBLYAI_API_KEY", "")
    MURF_API_KEY: str = os.getenv("MURF_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50000000"))  # 50MB
    MIN_AUDIO_SIZE: int = 1000  # 1KB minimum for valid audio

    # API Timeouts
    TIMEOUT_SECONDS: float = 30.0

    # Voice Mapping (Murf voice IDs)
    VOICE_MAPPING: dict = {
        "en-US-sarah": "en-US-samantha",
        "en-US-john": "en-US-cooper",
        "en-GB-emma": "en-UK-hazel",
        "en-US-david": "en-US-daniel",
        "en-US-jenny": "en-US-julia",
        "en-AU-william": "en-AU-shane"
    }

    # Chat Configuration
    MAX_CHAT_HISTORY: int = 20
    MAX_CONTEXT_MESSAGES: int = 10

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def is_api_key_valid(cls, api_key: Optional[str], key_name: str) -> bool:
        """Check if an API key is properly configured."""
        if not api_key:
            return False
        if api_key in ["your_actual_assemblyai_api_key_here", 
                       "your_actual_murf_api_key_here", 
                       "your_actual_gemini_api_key_here"]:
            return False
        return True

    @classmethod
    def validate_required_keys(cls) -> list:
        """Validate that required API keys are configured."""
        missing_keys = []
        
        if not cls.is_api_key_valid(cls.ASSEMBLYAI_API_KEY, "ASSEMBLYAI_API_KEY"):
            missing_keys.append("ASSEMBLYAI_API_KEY")
        
        if not cls.is_api_key_valid(cls.GEMINI_API_KEY, "GEMINI_API_KEY"):
            missing_keys.append("GEMINI_API_KEY")
            
        return missing_keys


# Create global settings instance
settings = Settings()
