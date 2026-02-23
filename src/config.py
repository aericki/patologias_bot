import os
import logging
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    google_api_key: str
    log_level: str = "INFO"
    gemini_model: str = "gemini-flash-latest"
    poll_interval: float = 2.0
    max_message_length: int = 3900


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_TOKEN", "")
    api_key = os.getenv("GOOGLE_API_KEY", "")

    if not token:
        raise ValueError("TELEGRAM_TOKEN não configurada no .env")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não configurada no .env")

    return Settings(
        telegram_token=token,
        google_api_key=api_key,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
    )


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
    )
