import logging
import sys
from datetime import datetime
from backend.config.settings import Config

def setup_logger():
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
    fh = logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger