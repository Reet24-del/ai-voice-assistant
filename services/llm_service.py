"""Google Gemini LLM service."""

import google.generativeai as genai
from fastapi import HTTPException

from config import settings
from utils import get_logger


class LLMService:
    """Service for handling LLM interactions using Google Gemini."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.model = None
        self._configure_api()
    
    def _configure_api(self):
        """Configure Google Gemini API with the API key."""
        if not settings.is_api_key_valid(settings.GEMINI_API_KEY, "GEMINI_API_KEY"):
            self.logger.error("Gemini API key not configured properly")
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured. Please add your Gemini API key to the .env file."
            )
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.logger.info("Google Gemini API configured successfully")
    
    async def generate_response(self, text: str) -> str:
        """
        Generate a response using Google Gemini.
        
        Args:
            text: Input text to send to the LLM
            
        Returns:
            Generated response text
        """
        self.logger.info(f"Generating LLM response for text length: {len(text)}")
        
        try:
            if not self.model:
                self._configure_api()
            
            # Generate response from the LLM
            response = self.model.generate_content(text)
            
            # Check if the response was successful
            if not response.text:
                self.logger.error("LLM returned empty response")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate response from Gemini API. The response was empty."
                )
            
            self.logger.info(f"LLM response generated successfully, length: {len(response.text)}")
            return response.text
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"LLM generation error: {str(e)}")
            
            # Handle specific Gemini API errors
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "invalid API key" in error_msg.lower():
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Gemini API key. Please check your API key configuration."
                )
            elif "QUOTA_EXCEEDED" in error_msg or "quota" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API quota exceeded. Please try again later."
                )
            elif "PERMISSION_DENIED" in error_msg:
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied. Please check your Gemini API key permissions."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process LLM query: {error_msg}"
                )
    
    async def generate_with_context(self, current_message: str, context: str = "") -> str:
        """
        Generate response with conversation context.
        
        Args:
            current_message: Current user message
            context: Previous conversation context
            
        Returns:
            Generated response text
        """
        if context:
            full_prompt = f"{context}Human: {current_message}"
        else:
            full_prompt = current_message
        
        self.logger.info(f"Generating contextual LLM response for prompt length: {len(full_prompt)}")
        return await self.generate_response(full_prompt)
