"""Language detection and management for multi-language support."""

import re
from typing import Literal, Tuple


class LanguageDetector:
    """
    Detects and manages language for input/output.

    Supports Japanese (ja) and English (en) detection using Unicode ranges
    and character frequency analysis.
    """

    # Unicode ranges for Japanese scripts
    HIRAGANA_RANGE = (0x3040, 0x309F)
    KATAKANA_RANGE = (0x30A0, 0x30FF)
    KANJI_RANGE = (0x4E00, 0x9FFF)
    FULLWIDTH_RANGE = (0xFF00, 0xFFEF)  # Full-width alphanumeric

    # Common Japanese punctuation
    JAPANESE_PUNCTUATION = "。、！？「」『』（）［］｛｝"

    CODE_FENCE_PATTERN = re.compile(r"```.*?```", re.DOTALL)
    """Matches fenced code blocks so they don't dominate detection."""

    INLINE_CODE_PATTERN = re.compile(r"`[^`]+`")
    """Matches inline code spans surrounded by backticks."""

    URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+)")
    """Matches bare URLs that otherwise skew English counts."""

    MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
    """Matches Markdown links and keeps only the label portion."""

    MULTI_WHITESPACE_PATTERN = re.compile(r"\s+")
    """Matches repeated whitespace for normalization."""

    def __init__(self, default_language: Literal["ja", "en"] = "ja"):
        """
        Initialize LanguageDetector.

        Args:
            default_language: Default language to use when detection is uncertain
        """
        self.default_language = default_language

    def is_japanese(self, text: str) -> bool:
        """
        Check if text contains Japanese characters.

        Args:
            text: Text to analyze

        Returns:
            True if Japanese characters are found, False otherwise
        """
        if not text:
            return False

        for char in text:
            code = ord(char)
            # Check if character is in any Japanese range
            if (self.HIRAGANA_RANGE[0] <= code <= self.HIRAGANA_RANGE[1] or
                self.KATAKANA_RANGE[0] <= code <= self.KATAKANA_RANGE[1] or
                self.KANJI_RANGE[0] <= code <= self.KANJI_RANGE[1] or
                char in self.JAPANESE_PUNCTUATION):
                return True

        return False

    def _count_japanese_chars(self, text: str) -> int:
        """
        Count the number of Japanese characters in text.

        Args:
            text: Text to analyze

        Returns:
            Number of Japanese characters
        """
        count = 0
        for char in text:
            code = ord(char)
            if (self.HIRAGANA_RANGE[0] <= code <= self.HIRAGANA_RANGE[1] or
                self.KATAKANA_RANGE[0] <= code <= self.KATAKANA_RANGE[1] or
                self.KANJI_RANGE[0] <= code <= self.KANJI_RANGE[1]):
                count += 1
        return count

    def _count_alphabet_chars(self, text: str) -> int:
        """
        Count the number of English alphabet characters in text.

        Args:
            text: Text to analyze

        Returns:
            Number of alphabet characters
        """
        return sum(1 for char in text if char.isalpha() and ord(char) < 128)

    def normalize_text(self, text: str) -> str:
        """
        Remove noise segments (code blocks, inline code, URLs) before detection.

        Example:
            >>> detector = LanguageDetector()
            >>> detector.normalize_text("See ```python\\nprint('hi')``` https://example.com")
            'See'
        """
        if not text:
            return ""

        # Remove Markdown links but keep labels
        cleaned = self.MARKDOWN_LINK_PATTERN.sub(r"\1", text)
        cleaned = self.CODE_FENCE_PATTERN.sub(" ", cleaned)
        cleaned = self.INLINE_CODE_PATTERN.sub(" ", cleaned)
        cleaned = self.URL_PATTERN.sub(" ", cleaned)
        cleaned = self.MULTI_WHITESPACE_PATTERN.sub(" ", cleaned)

        return cleaned.strip()

    def _prepare_text(self, text: str) -> str:
        """
        Normalize text and fall back to original content when everything is noise.
        """
        normalized = self.normalize_text(text)
        return normalized or (text or "")

    def get_confidence(self, text: str, language: Literal["ja", "en"]) -> float:
        """
        Return confidence score for detected language.

        The confidence is calculated based on the proportion of language-specific
        characters in the text.

        Args:
            text: Text to analyze
            language: Language to check confidence for

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not text or not text.strip():
            return 0.0

        # Remove whitespace for calculation
        prepared_text = self._prepare_text(text)
        text_cleaned = prepared_text.replace(" ", "").replace("\n", "").replace("\t", "")

        if not text_cleaned:
            return 0.0

        total_chars = len(text_cleaned)

        if language == "ja":
            japanese_chars = self._count_japanese_chars(text_cleaned)
            confidence = japanese_chars / total_chars if total_chars > 0 else 0.0
        else:  # en
            alphabet_chars = self._count_alphabet_chars(text_cleaned)
            confidence = alphabet_chars / total_chars if total_chars > 0 else 0.0

        return min(confidence, 1.0)

    def detect(self, text: str) -> Literal["ja", "en"]:
        """
        Detect language of input text.

        Uses character frequency analysis to determine if text is primarily
        Japanese or English. Falls back to default language if uncertain.

        Args:
            text: Text to analyze

        Returns:
            Detected language code ('ja' or 'en')

        Examples:
            >>> detector = LanguageDetector()
            >>> detector.detect("こんにちは")
            'ja'
            >>> detector.detect("Hello world")
            'en'
            >>> detector.detect("これはtest")  # Mixed
            'ja'  # If more Japanese chars
        """
        prepared_text = self._prepare_text(text)

        if not prepared_text or not prepared_text.strip():
            return self.default_language

        # Quick check: if any Japanese characters exist
        if not self.is_japanese(prepared_text):
            return "en"

        # Get confidence scores for both languages
        ja_confidence = self.get_confidence(prepared_text, "ja")
        en_confidence = self.get_confidence(prepared_text, "en")

        # If Japanese confidence is higher, it's Japanese
        if ja_confidence > en_confidence:
            return "ja"
        elif en_confidence > ja_confidence:
            return "en"
        else:
            # Equal or uncertain, use default
            return self.default_language

    def detect_with_confidence(self, text: str) -> Tuple[Literal["ja", "en"], float]:
        """
        Detect language and return confidence score.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (detected_language, confidence_score)

        Examples:
            >>> detector = LanguageDetector()
            >>> lang, conf = detector.detect_with_confidence("こんにちは世界")
            >>> lang
            'ja'
            >>> conf > 0.9
            True
        """
        detected_lang = self.detect(text)
        confidence = self.get_confidence(text, detected_lang)
        return detected_lang, confidence

    def get_prompt_template(self, language: Literal["ja", "en"]) -> str:
        """
        Get language-specific prompt template.

        Args:
            language: Target language

        Returns:
            Prompt template string with {query} placeholder
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

    def get_error_message(self, error_key: str, language: Literal["ja", "en"]) -> str:
        """
        Get localized error message.

        Args:
            error_key: Error message key
            language: Target language

        Returns:
            Localized error message
        """
        error_messages = {
            "ja": {
                "empty_query": "クエリが空です。質問を入力してください。",
                "invalid_model": "無効なモデル名です。",
                "session_error": "セッションの作成に失敗しました。",
                "unknown_error": "エラーが発生しました。"
            },
            "en": {
                "empty_query": "Query is empty. Please enter a question.",
                "invalid_model": "Invalid model name.",
                "session_error": "Failed to create session.",
                "unknown_error": "An error occurred."
            }
        }

        lang_messages = error_messages.get(language, error_messages[self.default_language])
        return lang_messages.get(error_key, lang_messages["unknown_error"])
