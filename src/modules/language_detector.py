"""Language detection and management for multi-language support."""

from typing import Literal


class LanguageDetector:
    """Detects and manages language for input/output."""

    def __init__(self, default_language: Literal["ja", "en"] = "ja"):
        """
        Initialize LanguageDetector.

        Args:
            default_language: Default language to use
        """
        self.default_language = default_language

    def detect(self, text: str) -> Literal["ja", "en"]:
        """
        Detect language of input text.

        Args:
            text: Text to analyze

        Returns:
            Detected language code ('ja' or 'en')
        """
        # TODO: Implement language detection
        # Simple heuristic: check for Japanese characters
        if any('\u3040' <= char <= '\u309F' or  # Hiragana
               '\u30A0' <= char <= '\u30FF' or  # Katakana
               '\u4E00' <= char <= '\u9FFF'     # Kanji
               for char in text):
            return "ja"
        return "en"

    def get_prompt_template(self, language: Literal["ja", "en"]) -> str:
        """
        Get language-specific prompt template.

        Args:
            language: Target language

        Returns:
            Prompt template string
        """
        templates = {
            "ja": "以下の質問に日本語で回答してください:\n\n{query}",
            "en": "Please answer the following question in English:\n\n{query}"
        }
        return templates.get(language, templates[self.default_language])

    def get_system_message(self, language: Literal["ja", "en"]) -> str:
        """
        Get language-specific system message.

        Args:
            language: Target language

        Returns:
            System message string
        """
        messages = {
            "ja": "あなたは研究者向けの分析アシスタントです。正確で詳細な情報を提供してください。",
            "en": "You are a research analyst assistant. Provide accurate and detailed information."
        }
        return messages.get(language, messages[self.default_language])
