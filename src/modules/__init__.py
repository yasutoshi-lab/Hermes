"""Hermes modules package."""

from .history_manager import HistoryManager
from .model_manager import (
    ModelManager,
    ModelNotFoundError,
    OllamaConnectionError
)
from .language_detector import LanguageDetector

__all__ = [
    "HistoryManager",
    "ModelManager",
    "ModelNotFoundError",
    "OllamaConnectionError",
    "LanguageDetector",
]
