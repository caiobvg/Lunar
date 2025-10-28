# src/utils/logger.py

import logging
import logging.handlers
import threading
import sys
import os
from datetime import datetime
from typing import Callable, List


class CustomLogger:
    def __init__(self, log_file: str = None):
        self.subscribers: List[Callable[[str], None]] = []
        self._lock = threading.RLock()

        # Setup python logging
        self.logger = logging.getLogger("MidnightSpoofer")
        self.logger.setLevel(logging.DEBUG)

        # Formatter: [HH:MM:SS] [LEVEL] [CONTEXT] Message
        fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(context)s] %(message)s", datefmt="%H:%M:%S")

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fmt)
        self.logger.addHandler(ch)

        # File handler (rotating) if requested
        if log_file is None:
            log_file = os.path.abspath(os.path.join(os.getcwd(), "midnight_log.txt"))
        fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)

    def add_subscriber(self, callback: Callable[[str], None]):
        """Register a GUI callback to receive formatted log strings."""
        with self._lock:
            if callback not in self.subscribers:
                self.subscribers.append(callback)

    def remove_subscriber(self, callback: Callable[[str], None]):
        with self._lock:
            if callback in self.subscribers:
                self.subscribers.remove(callback)

    def _notify_subscribers(self, record: logging.LogRecord):
        msg = self._format_record(record)
        with self._lock:
            for subscriber in list(self.subscribers):
                try:
                    subscriber(msg)
                except Exception:
                    # Subscribers must not break logging
                    pass

    def _format_record(self, record: logging.LogRecord) -> str:
        ctx = getattr(record, 'context', 'SYSTEM')
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        return f"[{timestamp}] [{record.levelname}] [{ctx}] {record.getMessage()}"

    def _log(self, level: int, message: str, context: str = "SYSTEM"):
        extra = {'context': context}
        # Use the underlying logger to handle handlers
        self.logger.log(level, message, extra=extra)
        # Also notify subscribers with formatted message
        record = logging.LogRecord(name=self.logger.name, level=level, pathname=__file__, lineno=0, msg=message, args=(), exc_info=None)
        setattr(record, 'context', context)
        self._notify_subscribers(record)

    # Public convenience methods
    def debug(self, message: str, context: str = "SYSTEM"):
        self._log(logging.DEBUG, message, context)

    def info(self, message: str, context: str = "SYSTEM"):
        self._log(logging.INFO, message, context)

    def success(self, message: str, context: str = "SYSTEM"):
        # No native success level — use INFO with SUCCESS context
        self._log(logging.INFO, message, context)

    def warning(self, message: str, context: str = "WARNING"):
        self._log(logging.WARNING, message, context)

    def error(self, message: str, context: str = "ERROR"):
        self._log(logging.ERROR, message, context)

    def exception(self, message: str, context: str = "ERROR"):
        # Log exception with stack trace
        self.logger.exception(message, extra={'context': context})
        # Notify subscribers as well
        record = logging.LogRecord(name=self.logger.name, level=logging.ERROR, pathname=__file__, lineno=0, msg=message, args=(), exc_info=None)
        setattr(record, 'context', context)
        self._notify_subscribers(record)

    # Backwards-compatible wrappers for previous API
    def log(self, message: str, level: str = "INFO", context: str = "SYSTEM"):
        """Compatibility wrapper: log(message, level, context)"""
        lvl = (level or "INFO").upper()
        if lvl == "DEBUG":
            self.debug(message, context)
        elif lvl in ("INFO",):
            self.info(message, context)
        elif lvl in ("SUCCESS",):
            self.success(message, context)
        elif lvl in ("WARNING", "WARN"):
            self.warning(message, context)
        elif lvl in ("ERROR",):
            self.error(message, context)
        elif lvl in ("CRITICAL",):
            self.error(message, context)
        else:
            self.info(message, context)

    def log_info(self, message: str, context: str = "SYSTEM"):
        self.info(message, context)

    def log_success(self, message: str, context: str = "SUCCESS"):
        self.success(message, context)

    def log_warning(self, message: str, context: str = "WARNING"):
        self.warning(message, context)

    def log_error(self, message: str, context: str = "ERROR"):
        self.error(message, context)

    def log_critical(self, message: str, context: str = "CRITICAL"):
        self.error(message, context)


# Global logger instance
logger = CustomLogger()