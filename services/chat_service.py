"""Chat history management service."""

from typing import List, Dict, Any
from datetime import datetime

from config import settings
from utils import get_logger


class ChatService:
    """Service for managing chat history and conversation state."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        # In-memory chat history datastore
        # Key: session_id, Value: list of messages
        self.chat_history_store: Dict[str, List[Dict[str, Any]]] = {}
    
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get chat history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of chat messages
        """
        history = self.chat_history_store.get(session_id, [])
        self.logger.info(f"Retrieved {len(history)} messages for session {session_id}")
        return history
    
    def add_to_chat_history(self, session_id: str, role: str, content: str):
        """
        Add a message to chat history.
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        timestamp = datetime.now().isoformat()
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        
        if session_id not in self.chat_history_store:
            self.chat_history_store[session_id] = []
        
        self.chat_history_store[session_id].append(message)
        
        # Keep only the last MAX_CHAT_HISTORY messages to prevent memory issues
        if len(self.chat_history_store[session_id]) > settings.MAX_CHAT_HISTORY:
            self.chat_history_store[session_id] = self.chat_history_store[session_id][-settings.MAX_CHAT_HISTORY:]
        
        self.logger.info(f"Added {role} message to session {session_id}, total messages: {len(self.chat_history_store[session_id])}")
    
    def format_chat_history_for_llm(self, chat_history: List[Dict[str, Any]]) -> str:
        """
        Format chat history for LLM context.
        
        Args:
            chat_history: List of chat messages
            
        Returns:
            Formatted string for LLM context
        """
        if not chat_history:
            return ""
        
        formatted_history = "Previous conversation:\\n"
        
        # Use only last MAX_CONTEXT_MESSAGES for context to avoid token limits
        recent_history = chat_history[-settings.MAX_CONTEXT_MESSAGES:]
        
        for message in recent_history:
            role = "Human" if message["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {message['content']}\\n"
        
        formatted_history += "\\nCurrent message:\\n"
        
        self.logger.info(f"Formatted {len(recent_history)} messages for LLM context")
        return formatted_history
    
    def clear_chat_history(self, session_id: str) -> bool:
        """
        Clear chat history for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if history existed and was cleared, False otherwise
        """
        if session_id in self.chat_history_store:
            message_count = len(self.chat_history_store[session_id])
            del self.chat_history_store[session_id]
            self.logger.info(f"Cleared {message_count} messages for session {session_id}")
            return True
        else:
            self.logger.info(f"No chat history found for session {session_id}")
            return False
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a chat session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session information
        """
        history = self.get_chat_history(session_id)
        
        if not history:
            return {
                "session_id": session_id,
                "message_count": 0,
                "created_at": None,
                "last_activity": None
            }
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "created_at": history[0]["timestamp"] if history else None,
            "last_activity": history[-1]["timestamp"] if history else None
        }
    
    def get_all_sessions(self) -> List[str]:
        """
        Get list of all active session IDs.
        
        Returns:
            List of session IDs
        """
        sessions = list(self.chat_history_store.keys())
        self.logger.info(f"Retrieved {len(sessions)} active sessions")
        return sessions
