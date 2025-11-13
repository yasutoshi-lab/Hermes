"""LLM node for generating provisional answers with structured citations."""

from __future__ import annotations

import logging
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from config import settings
from modules.model_manager import (
    ModelManager,
    ModelNotFoundError,
    OllamaConnectionError,
)
from state.agent_state import AgentState, add_error
from .utils.prompt_builder import PromptBundle, build_llm_prompt

logger = logging.getLogger(__name__)

StreamCallback = Callable[[str], None]


def _normalize_language(value: Optional[str]) -> str:
    return "ja" if value == "ja" else "en"


def _resolve_model_manager(state: AgentState) -> ModelManager:
    candidate = state.get("model_manager")
    if candidate and hasattr(candidate, "generate"):
        return candidate  # type: ignore[return-value]
    try:
        return ModelManager()
    except ImportError as exc:
        raise RuntimeError(
            "ModelManager requires the 'ollama' package. Install it to enable LLM generation."
        ) from exc


def _resolve_stream_callback(state: AgentState) -> Optional[StreamCallback]:
    for key in ("llm_stream_callback", "stream_callback"):
        candidate = state.get(key)  # type: ignore[index]
        if callable(candidate):
            return candidate  # type: ignore[return-value]
    return None


def _coerce_processed_entries(state: AgentState) -> List[Dict[str, Any]]:
    processed = state.get("processed_data") or []
    if processed:
        return [entry for entry in processed if isinstance(entry, dict)]

    fallback_entries: List[Dict[str, Any]] = []
    for result in state.get("search_results") or []:
        if not isinstance(result, dict):
            continue
        fallback_entries.append(
            {
                "source": {
                    "title": result.get("title", "Search Result"),
                    "url": result.get("url", ""),
                },
                "summary": result.get("summary") or result.get("description") or "",
                "key_facts": [
                    textwrap.shorten(str(result.get("content", "")), width=240, placeholder="…")
                ],
            }
        )
    return fallback_entries


def _invoke_model(
    manager: ModelManager,
    model_name: str,
    bundle: PromptBundle,
    stream_callback: Optional[StreamCallback],
) -> str:
    system_prompt = manager.get_system_prompt(bundle.language, task_type="research")
    if stream_callback:
        chunks: List[str] = []
        for token in manager.generate_streaming(
            model_name=model_name,
            prompt=bundle.prompt,
            system_prompt=system_prompt,
            temperature=0.6,
        ):
            chunks.append(token)
            try:
                stream_callback(token)
            except Exception as exc:  # pragma: no cover - defensive logging only
                logger.warning("LLMNode: stream callback raised %s; continuing", exc)
        return "".join(chunks).strip()

    return manager.generate(
        model_name=model_name,
        prompt=bundle.prompt,
        system_prompt=system_prompt,
        temperature=0.6,
        max_tokens=1800,
    ).strip()


def _persist_llm_summary(
    history_path: str,
    provisional_answer: str,
    bundle: PromptBundle,
    metadata: Dict[str, Any],
) -> Optional[str]:
    if not history_path:
        return None

    session_path = Path(history_path)
    if not session_path.exists():
        return None

    summary_file = session_path / "llm_summary.md"
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        lines = [
            f"## LLM Draft - {timestamp}",
            "",
            "### Context Summary",
            bundle.context_summary or "(no context)",
            "",
            "### Provisional Answer (excerpt)",
            textwrap.shorten(provisional_answer, width=600, placeholder="…"),
            "",
            "### Citations",
        ]
        for citation in metadata.get("citations", []):
            title = citation.get("title", "Untitled Source")
            url = citation.get("url", "")
            lines.append(f"- [{citation.get('id', '?')}] {title} {url}".rstrip())
        lines.append("")

        with summary_file.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines))

        return str(summary_file)
    except OSError as exc:
        logger.warning("LLMNode: Failed to persist llm_summary.md: %s", exc)
        return None


def llm_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate analysis and provisional answer using the configured LLM.

    The node builds a localized prompt that summarizes processed data with
    citations, calls the Ollama-backed ModelManager, streams partial outputs
    when requested, and persists a summary artifact for downstream nodes.
    """
    query = state.get("query", "").strip()
    if not query:
        return add_error(state, "LLMNode: query is required before generation")

    context_entries = _coerce_processed_entries(state)
    if not context_entries:
        return add_error(state, "LLMNode: No processed data or search results available")

    language = _normalize_language(state.get("language"))
    model_name = (state.get("model_name") or settings.default_model).strip() or settings.default_model
    stream_callback = _resolve_stream_callback(state)

    try:
        manager = _resolve_model_manager(state)
    except RuntimeError as exc:
        return add_error(state, f"LLMNode: {exc}")

    languages_to_try = [language]
    if language != "en":
        languages_to_try.append("en")

    max_context = min(len(context_entries), 6) or 1
    collected_errors: List[str] = []

    for lang in languages_to_try:
        context_limit = max_context
        while context_limit > 0:
            bundle = build_llm_prompt(
                query,
                context_entries,
                lang,
                max_sources=context_limit,
                max_facts_per_source=3,
            )
            try:
                provisional_answer = _invoke_model(manager, model_name, bundle, stream_callback)
                if not provisional_answer:
                    raise OllamaConnectionError("Model returned empty response")

                metadata = {
                    "model": model_name,
                    "language": lang,
                    "context_items": min(context_limit, len(context_entries)),
                    "prompt_length": len(bundle.prompt),
                    "citations": bundle.citations,
                }
                history_log = _persist_llm_summary(state.get("history_path", ""), provisional_answer, bundle, metadata)
                if history_log:
                    metadata["history_log"] = history_log

                update: Dict[str, Any] = {
                    "provisional_answer": provisional_answer,
                    "llm_metadata": metadata,
                    "messages": [
                        {
                            "role": "assistant",
                            "content": (
                                f"Generated provisional answer using {model_name} "
                                f"({metadata['context_items']} sources, language={lang})."
                            ),
                        }
                    ],
                }

                if collected_errors:
                    update["errors"] = state.get("errors", []) + collected_errors

                return update

            except (ModelNotFoundError, OllamaConnectionError, RuntimeError) as exc:
                message = f"LLMNode: generation failed (lang={lang}, sources={context_limit}): {exc}"
                logger.warning(message)
                collected_errors.append(message)
                context_limit = context_limit // 2

    final_error = "LLMNode: Unable to generate provisional answer after retries"
    collected_errors.append(final_error)
    return {"errors": state.get("errors", []) + collected_errors}


__all__ = ["llm_node"]
