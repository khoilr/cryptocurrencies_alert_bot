"""Config logger"""
from datetime import datetime

from loguru import logger

logger.add(
    f"logs/{datetime.utcnow().isoformat()}.log",
    rotation="100 MB",
    retention="1 month",
)
