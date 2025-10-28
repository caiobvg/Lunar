# src/utils/logger.py

import logging
import sys
from datetime import datetime
from typing import Callable, List

class CustomLogger:
    def __init__(self):
        self.subscribers: List[Callable[[str], None]] = []
        
        # Mapa de cores para diferentes contextos
        self.context_colors = {
            "SYSTEM": "#6b21ff",
            "SECURITY": "#00ff88", 
            "HARDWARE": "#ffaa00",
            "MAC": "#b0b0ff",  # ← ADICIONADO: Cor para logs MAC
            "ERROR": "#ff4444",
            "SUCCESS": "#00ff88",
            "WARNING": "#ffaa00",
            "INFO": "#e0e0ff",
            "CONTROL": "#6b21ff",
            "SPOOFING": "#ff55ff",
            "NETWORK": "#55aaff",
            "REGISTRY": "#ffaa55",
            "USER": "#aa55ff",
            "NAVIGATION": "#55ffaa",
            "CRITICAL": "#ff4444"
        }

    def add_subscriber(self, callback: Callable[[str], None]):
        """Add a subscriber to receive log messages"""
        if callback not in self.subscribers:
            self.subscribers.append(callback)

    def remove_subscriber(self, callback: Callable[[str], None]):
        """Remove a subscriber"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def _notify_subscribers(self, message: str):
        """Notify all subscribers with the log message"""
        for subscriber in self.subscribers:
            try:
                subscriber(message)
            except Exception as e:
                # Prevent logging errors from breaking the application
                print(f"Subscriber error: {e}")

    def _format_message(self, message: str, level: str, context: str) -> str:
        """Format log message with timestamp and context"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Get color for context or use default
        color_code = self.context_colors.get(context, "#e0e0ff")
        
        # Format: [TIME] [LEVEL] [CONTEXT] Message
        formatted = f"[{timestamp}] [{level}] [{context}] {message}"
        return formatted

    def log(self, message: str, level: str = "INFO", context: str = "SYSTEM"):
        """Main logging method"""
        formatted_message = self._format_message(message, level, context)
        
        # Print to console
        print(formatted_message)
        
        # Notify subscribers (like GUI)
        self._notify_subscribers(formatted_message)

    # Convenience methods
    def log_info(self, message: str, context: str = "SYSTEM"):
        self.log(message, "INFO", context)

    def log_success(self, message: str, context: str = "SUCCESS"):
        self.log(message, "SUCCESS", context)

    def log_warning(self, message: str, context: str = "WARNING"):
        self.log(message, "WARNING", context)

    def log_error(self, message: str, context: str = "ERROR"):
        self.log(message, "ERROR", context)

    def log_critical(self, message: str, context: str = "CRITICAL"):
        self.log(message, "CRITICAL", context)

# Global logger instance
logger = CustomLogger()