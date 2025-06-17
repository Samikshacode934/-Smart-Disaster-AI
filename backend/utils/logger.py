import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to Python path (more reliable than sys.path.append)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.config.settings import Config

def setup_logger():
    # Create logs directory if not exists
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(Config.LOG_LEVEL)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    log_file = f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info(f"Logger initialized. Log file: {log_file}")
    return logger

if __name__ == "__main__":
    logger = setup_logger()
    logger.info("Logger test successful")