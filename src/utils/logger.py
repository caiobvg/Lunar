# src/utils/logger.py
import logging
import sys
from datetime import datetime
from typing import Callable, List
from colorama import Fore, Style, init

# Initialize colorama for Windows colors
init()

class MidnightLogger:
    def __init__(self):
        self.logger = logging.getLogger('MidnightSpoofer')
        self.logger.setLevel(logging.INFO)
        self.subscribers: List[Callable] = []
        
        # Consistent log format
        formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler('midnight_log.txt', encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def add_subscriber(self, callback: Callable):
        """Add GUI or other components as log subscribers"""
        self.subscribers.append(callback)
    
    def _notify_subscribers(self, message: str, level: str):
        """Notify all subscribers with formatted message"""
        formatted_message = self._format_message(message, level)
        for subscriber in self.subscribers:
            try:
                subscriber(formatted_message)
            except Exception as e:
                # Fallback if subscriber fails
                print(f"Subscriber error: {e}")
    
    def _format_message(self, message: str, level: str) -> str:
        """Format message consistently for all outputs"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        return f"[{timestamp}] [{level}] {message}"
    
    def log_info(self, message: str, context: str = "SYSTEM"):
        """Log info level message"""
        formatted = self._format_message(message, "INFO")
        try:
            self.logger.info(f"[{context}] {message}")
        except Exception as e:
            print(f"LOG FALLBACK: {message}")
        
        self._notify_subscribers(f"[{context}] {message}", "INFO")
        return formatted
    
    def log_success(self, message: str, context: str = "SYSTEM"):
        """Log success level message"""
        formatted = self._format_message(message, "SUCCESS")
        try:
            self.logger.info(f"[{context}] {message}")
        except Exception as e:
            print(f"LOG FALLBACK: {message}")
        
        self._notify_subscribers(f"[{context}] {message}", "SUCCESS")
        return formatted
    
    def log_warning(self, message: str, context: str = "SYSTEM"):
        """Log warning level message"""
        formatted = self._format_message(message, "WARNING")
        try:
            self.logger.warning(f"[{context}] {message}")
        except Exception as e:
            print(f"LOG FALLBACK: {message}")
        
        self._notify_subscribers(f"[{context}] {message}", "WARNING")
        return formatted
    
    def log_error(self, message: str, context: str = "SYSTEM"):
        """Log error level message"""
        formatted = self._format_message(message, "ERROR")
        try:
            self.logger.error(f"[{context}] {message}")
        except Exception as e:
            print(f"LOG FALLBACK: {message}")
        
        self._notify_subscribers(f"[{context}] {message}", "ERROR")
        return formatted
    
    def log_debug(self, message: str, context: str = "SYSTEM"):
        """Log debug level message"""
        formatted = self._format_message(message, "DEBUG")
        try:
            self.logger.debug(f"[{context}] {message}")
        except Exception as e:
            print(f"LOG FALLBACK: {message}")
        
        self._notify_subscribers(f"[{context}] {message}", "DEBUG")
        return formatted

# Global logger instance
logger = MidnightLogger()