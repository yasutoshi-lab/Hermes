"""Tests for LanguageDetector heuristics and outputs."""

import sys
from pathlib import Path

import pytest

# Ensure src is importable when running pytest from repo root
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from modules.language_detector import LanguageDetector  # type: ignore  # noqa: E402


@pytest.fixture
def detector() -> LanguageDetector:
    return LanguageDetector(default_language="ja")


def test_detect_japanese_text(detector: LanguageDetector) -> None:
    text = "LangGraphとは何ですか？ 最新情報を教えてください。"
    assert detector.detect(text) == "ja"


def test_detect_english_with_code_blocks(detector: LanguageDetector) -> None:
    text = """Please review the snippet below:\n```python\nprint('こんにちは')\n```\nhttps://example.com"""
    assert detector.detect(text) == "en"


def test_is_japanese_handles_unicode(detector: LanguageDetector) -> None:
    assert detector.is_japanese("テスト文章です。") is True
    assert detector.is_japanese("Plain text only.") is False


def test_get_confidence_returns_fraction(detector: LanguageDetector) -> None:
    confidence = detector.get_confidence("LangGraphについて詳しく", "ja")
    assert 0.0 < confidence <= 1.0


def test_prompt_templates_are_localized(detector: LanguageDetector) -> None:
    ja_template = detector.get_prompt_template("ja")
    en_template = detector.get_prompt_template("en")
    assert "日本語" in ja_template
    assert "English" in en_template


def test_normalize_text_removes_noise(detector: LanguageDetector) -> None:
    noisy = "See ```javascript console.log('hi')``` at https://example.com/docs"
    cleaned = detector.normalize_text(noisy)
    assert "console.log" not in cleaned
    assert "https://" not in cleaned
