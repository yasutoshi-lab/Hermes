"""Helpers for formatting source citations shared by LLM and report nodes."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Sequence
import textwrap


def _short_summary(text: str, *, width: int = 200) -> str:
    return textwrap.shorten(" ".join(text.split()), width=width, placeholder="…") if text else ""


def _add_source(registry: "OrderedDict[str, Dict[str, str]]", title: str, url: str, summary: str) -> None:
    key = url or title
    if not key or key in registry:
        return
    registry[key] = {
        "title": title or "Untitled Source",
        "url": url,
        "summary": summary,
    }


def _processed_to_sources(entries: Sequence[Dict[str, Any]]) -> Iterable[Dict[str, str]]:
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        source = entry.get("source") or {}
        if isinstance(source, str):
            source = {"title": source}
        title = source.get("title") or source.get("url") or "Processed Source"
        url = source.get("url", "")
        summary = entry.get("summary") or ""
        if not summary:
            key_facts = entry.get("key_facts") or []
            for fact in key_facts:
                if isinstance(fact, str) and fact.strip():
                    summary = fact.strip()
                    break
        if not summary and entry.get("normalized_content"):
            summary = str(entry["normalized_content"]).splitlines()[0]
        yield {
            "title": title,
            "url": url,
            "summary": _short_summary(summary),
        }


def _search_to_sources(results: Sequence[Dict[str, Any]]) -> Iterable[Dict[str, str]]:
    for result in results:
        if not isinstance(result, dict):
            continue
        title = result.get("title") or result.get("url") or "Search Result"
        url = result.get("url", "")
        summary = result.get("summary") or result.get("description") or result.get("content", "")
        yield {
            "title": title,
            "url": url,
            "summary": _short_summary(str(summary)),
        }


def format_sources(
    search_results: Sequence[Dict[str, Any]],
    processed_data: Sequence[Dict[str, Any]],
    *,
    max_sources: int = 10
) -> Dict[str, Any]:
    """
    Deduplicate and format citations from processed data and fallback to raw search hits.

    Returns:
        Dict with:
            - items: ordered list of {'id','title','url','summary'}
            - markdown: bullet list string for Markdown sections
    """
    registry: "OrderedDict[str, Dict[str, str]]" = OrderedDict()

    for entry in _processed_to_sources(processed_data):
        if len(registry) >= max_sources:
            break
        _add_source(registry, entry["title"], entry["url"], entry["summary"])

    if len(registry) < max_sources:
        for entry in _search_to_sources(search_results):
            if len(registry) >= max_sources:
                break
            _add_source(registry, entry["title"], entry["url"], entry["summary"])

    items: List[Dict[str, str]] = []
    markdown_lines: List[str] = []
    for idx, source in enumerate(registry.values(), start=1):
        cite_id = f"S{idx}"
        item = {
            "id": cite_id,
            "title": source["title"],
            "url": source["url"],
            "summary": source["summary"],
        }
        items.append(item)
        url_segment = f" ({source['url']})" if source["url"] else ""
        summary_segment = f" — {source['summary']}" if source["summary"] else ""
        markdown_lines.append(f"- [{cite_id}] {source['title']}{url_segment}{summary_segment}")

    markdown = "\n".join(markdown_lines) if markdown_lines else "- (no sources available)"
    return {"items": items, "markdown": markdown}


__all__ = ["format_sources"]
