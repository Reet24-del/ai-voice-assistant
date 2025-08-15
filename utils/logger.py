"""Centralized logging utility for the application."""

import logging
import sys
from pathlib import Path
from config import settings


class Logger:
    """Centralized logger configuration."""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger instance."""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            
            # Only configure if logger doesn't have handlers
            if not logger.handlers:
                logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
                
                # Create console handler
                handler = logging.StreamHandler(sys.stdout)
                handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
                
                # Create formatter
                formatter = logging.Formatter(settings.LOG_FORMAT)
                handler.setFormatter(formatter)
                
                # Add handler to logger
                logger.addHandler(handler)
                
                # Prevent duplicate logging
                logger.propagate = False
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]


# Convenience function to get a logger
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return Logger.get_logger(name)
