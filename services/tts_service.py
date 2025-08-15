"""Murf TTS (Text-to-Speech) service."""

import httpx
from fastapi import HTTPException

from config import settings
from utils import get_logger


class TTSService:
    """Service for handling text-to-speech using Murf AI."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.api_url = "https://api.murf.ai/v1/speech/generate"
    
    def _validate_api_key(self):
        """Validate that Murf API key is configured."""
        if not settings.is_api_key_valid(settings.MURF_API_KEY, "MURF_API_KEY"):
            self.logger.error("Murf API key not configured properly")
            raise HTTPException(
                status_code=500,
                detail="MURF_API_KEY not configured properly. Please add your real Murf API key to the .env file. Use 'fastapi_server_mock.py' for testing without an API key."
            )
    
    def _get_murf_voice(self, voice_id: str) -> str:
        """
        Map friendly voice ID to actual Murf voice ID.
        
        Args:
            voice_id: Friendly voice identifier
            
        Returns:
            Actual Murf voice ID
        """
        return settings.VOICE_MAPPING.get(voice_id, "en-US-samantha")
    
    def _calculate_murf_rate(self, speed: int) -> int:
        """
        Convert speed percentage to Murf rate.
        
        Args:
            speed: Speed percentage (50-150)
            
        Returns:
            Murf rate (-50 to 50)
        """
        # Convert speed percentage (50-150) to Murf rate (-50 to 50)
        murf_rate = (speed - 100) // 2
        return max(-50, min(50, murf_rate))  # Clamp to valid range
    
    async def generate_speech(self, text: str, voice_id: str = "en-US-sarah", speed: int = 100) -> str:
        """
        Generate speech from text using Murf AI.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice identifier
            speed: Speech speed percentage (50-150)
            
        Returns:
            Audio URL or base64 data URL
        """
        self._validate_api_key()
        
        murf_voice = self._get_murf_voice(voice_id)
        murf_rate = self._calculate_murf_rate(speed)
        
        headers = {
            "api-key": settings.MURF_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "voiceId": murf_voice,
            "rate": murf_rate,
            "sampleRate": 48000,
            "format": "MP3",
            "channelType": "MONO"
        }
        
        self.logger.info(f"Generating TTS for text length: {len(text)}, voice: {murf_voice}, rate: {murf_rate}")
        
        try:
            async with httpx.AsyncClient(timeout=settings.TIMEOUT_SECONDS) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract audio URL or data
                    audio_url = result.get("audioFile", result.get("url", ""))
                    
                    if not audio_url:
                        # If no direct URL, create a data URL from base64 audio data
                        audio_data = result.get("audioContent", "")
                        if audio_data:
                            audio_url = f"data:audio/mp3;base64,{audio_data}"
                    
                    if not audio_url:
                        raise HTTPException(
                            status_code=500,
                            detail="Murf API did not return audio data"
                        )
                    
                    self.logger.info("TTS generation completed successfully")
                    return audio_url
                    
                else:
                    error_detail = response.text if response.text else "Unknown error"
                    self.logger.error(f"Murf API error: {response.status_code} - {error_detail}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Murf API error: {error_detail}"
                    )
                    
        except httpx.TimeoutException:
            self.logger.error("Request to Murf API timed out")
            raise HTTPException(
                status_code=408,
                detail="Request to Murf API timed out"
            )
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"TTS generation error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate TTS: {str(e)}"
            )
    
    async def generate_speech_legacy(self, text: str, voice_id: str = "en-US-sarah", speed: int = 100) -> str:
        """
        Legacy method for TTS generation using Bearer token format.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice identifier
            speed: Speech speed percentage
            
        Returns:
            Audio URL
        """
        self._validate_api_key()
        
        headers = {
            "Authorization": f"Bearer {settings.MURF_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "voice_id": voice_id,
            "speed": speed,
            "format": "mp3"
        }
        
        try:
            async with httpx.AsyncClient(timeout=settings.TIMEOUT_SECONDS) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    audio_url = result.get("audio_url", "")
                    
                    if not audio_url:
                        raise HTTPException(
                            status_code=500,
                            detail="Murf API did not return audio URL"
                        )
                    
                    return audio_url
                    
                else:
                    error_detail = response.text if response.text else "Unknown error"
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Murf API error: {error_detail}"
                    )
                    
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=408,
                detail="Request to Murf API timed out"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate TTS: {str(e)}"
            )
