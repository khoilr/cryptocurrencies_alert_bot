"""Logger configuration for the project."""

from datetime import datetime

from loguru import logger

logger.add(f"logs/telegram_bot_{datetime.now().isoformat()}.log", rotation="500 MB")
