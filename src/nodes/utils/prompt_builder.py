"""Prompt assembly helpers for the LLM node."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence
import textwrap


@dataclass(slots=True)
class PromptBundle:
    """Container with the rendered prompt and supporting metadata."""

    prompt: str
    context_summary: str
    citations: List[Dict[str, str]]
    language: str


def _shorten(text: str, *, width: int = 220) -> str:
    """Return a compact, single-line summary of the provided text."""
    if not text:
        return ""
    return textwrap.shorten(" ".join(text.split()), width=width, placeholder="…")


def _normalize_entry(raw_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize processed data entries into a predictable structure."""
    source = raw_entry.get("source") or {}
    if isinstance(source, str):
        source = {"title": source}

    title = source.get("title") or source.get("url") or "Untitled Source"
    url = source.get("url", "")

    key_facts: Sequence[str] = raw_entry.get("key_facts") or []
    facts = [fact.strip() for fact in key_facts if isinstance(fact, str) and fact.strip()]

    if not facts:
        summary = raw_entry.get("summary") or raw_entry.get("normalized_content", "")
        summary_text = _shorten(str(summary)) if summary else ""
        if summary_text:
            facts = [summary_text]

    if not facts:
        snippets = raw_entry.get("snippets") or []
        for snippet in snippets:
            text = ""
            if isinstance(snippet, dict):
                text = snippet.get("text", "")
            elif isinstance(snippet, str):
                text = snippet
            text = _shorten(text)
            if text:
                facts.append(text)
            if len(facts) >= 2:
                break

    return {
        "title": title.strip(),
        "url": url.strip(),
        "facts": facts[:5],
    }


def build_llm_prompt(
    query: str,
    processed_entries: Sequence[Dict[str, Any]],
    language: str,
    *,
    max_sources: int = 5,
    max_facts_per_source: int = 3
) -> PromptBundle:
    """Build a localized prompt that summarizes processed data with citations."""
    normalized_language = "ja" if language == "ja" else "en"

    limited_entries = list(processed_entries)[:max_sources] or [{
        "source": {"title": "No context"},
        "summary": "No processed data was available; respond with best effort.",
    }]

    citations: List[Dict[str, str]] = []
    bullet_lines: List[str] = []

    for idx, entry in enumerate(limited_entries, start=1):
        normalized = _normalize_entry(entry)
        cite_id = f"S{idx}"
        citations.append({
            "id": cite_id,
            "title": normalized["title"],
            "url": normalized["url"],
        })

        fact_text = "; ".join(normalized["facts"][:max_facts_per_source]) or "No summary provided"
        url_segment = f" ({normalized['url']})" if normalized["url"] else ""
        bullet_lines.append(f"- [{cite_id}] {normalized['title']}: {fact_text}{url_segment}")

    context_summary = "\n".join(bullet_lines) if bullet_lines else "- (context unavailable)"

    if normalized_language == "ja":
        preface = (
            "あなたは厳密な一次情報に基づき回答するリサーチアシスタントです。"
            "以下の証拠のみを使い、日本語で箇条書き中心の暫定回答を作成してください。"
        )
        guidance = (
            "1. 150〜250語程度の概要段落から開始し、文末に引用ラベル [S1] のように付与する。\n"
            "2. \"Key Findings\" セクションで最重要な論点を3〜5項目示し、各項目で根拠ラベルを明示する。\n"
            "3. \"Verification Targets\" として、追加確認が必要な点を2項目まで列挙する。\n"
            "4. 記載のない事実は推測しない。数値や固有名詞には必ず引用を付ける。"
        )
    else:
        preface = (
            "You are a research analyst constrained to the evidence below. "
            "Write a concise provisional answer in English and cite sources like [S2]."
        )
        guidance = (
            "1. Start with a 2-3 sentence overview and attach citation labels (e.g., [S1]).\n"
            "2. Provide a \"Key Findings\" section listing 3-5 bullets with explicit citations.\n"
            "3. Add a \"Verification Targets\" section with up to two follow-up checks that remain open.\n"
            "4. Avoid speculation or new facts that are not grounded in the provided evidence."
        )

    prompt = "\n\n".join([
        preface,
        "### Query",
        query.strip() or "(query missing)",
        "### Evidence Summary",
        context_summary,
        "### Instructions",
        guidance,
    ])

    return PromptBundle(
        prompt=prompt,
        context_summary=context_summary,
        citations=citations,
        language=normalized_language,
    )


__all__ = ["PromptBundle", "build_llm_prompt"]
