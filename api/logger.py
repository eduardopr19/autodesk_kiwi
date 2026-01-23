import logging
import sys
from datetime import datetime

def setup_logger(name: str = "autodesk") -> logging.Logger:
    """Configure un logger avec formatage coloré"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Handler console
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Format avec couleurs
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
        }
        RESET = '\033[0m'
        
        def format(self, record):
            color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            return super().format(record)
    
    formatter = ColoredFormatter(
        '%(levelname)s | %(asctime)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger