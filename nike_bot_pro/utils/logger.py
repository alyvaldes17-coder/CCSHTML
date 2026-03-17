# utils/logger.py
import logging
import os
import sys
from datetime import datetime

class HumanFormatter(logging.Formatter):
    """Formateador con emojis para legibilidad humana"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }
    
    def format(self, record):
        # Nivel con emoji
        emoji = self.EMOJIS.get(record.levelname, '•')
        level = record.levelname
        
        # Timestamp humanizado
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        
        # Mensaje
        msg = record.getMessage()
        
        # Colorear en consola (si aplica)
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            formatted = f"{color}[{timestamp}] {emoji} [{record.name}] {msg}{reset}"
        else:
            formatted = f"[{timestamp}] {emoji} [{record.name}] {msg}"
        
        # Excepción si aplica
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)
        
        return formatted


def setup_logger(name: str, level: str = "INFO"):
    """Setup logger con formato humanizado y emojis"""
    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_file = os.path.join("logs", f"{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    # Evitar handlers duplicados
    if logger.handlers:
        return logger

    # Formateador humanizado
    formatter = HumanFormatter()

    # File handler (sin color)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(formatter)

    # Console handler (con color)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
