# src/utils/logger.py
import logging
import sys
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for Windows colors
init()

class MidnightLogger:
    def __init__(self):
        self.logger = logging.getLogger('MidnightSpoofer')
        self.logger.setLevel(logging.INFO)
        
        # More technical log format
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler('midnight_log.txt', encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log_info(self, message):
        self.logger.info(f"{message}")
        return f"[INFO] {message}"
    
    def log_success(self, message):
        self.logger.info(f"{message}")
        return f"[SUCCESS] {message}"
    
    def log_warning(self, message):
        self.logger.warning(f"{message}")
        return f"[WARNING] {message}"
    
    def log_error(self, message):
        self.logger.error(f"{message}")
        return f"[ERROR] {message}"
    
    def log_debug(self, message):
        self.logger.debug(f"{message}")
        return f"[DEBUG] {message}"

# Global logger instance
logger = MidnightLogger()