"""Report node for generating localized Markdown/PDF deliverables."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List

from config import settings
from modules.history_manager import HistoryManager, HistoryManagerError
from state.agent_state import AgentState, add_error
from .utils.source_formatting import format_sources

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    REPORTLAB_AVAILABLE = True
except Exception:  # pragma: no cover - handled gracefully in tests
    REPORTLAB_AVAILABLE = False


def _normalize_language(value: Optional[str]) -> str:
    return "ja" if value == "ja" else "en"


def _render_methodology(language: str) -> str:
    if language == "ja":
        return (
            "- 入力ノード: クエリ整形と言語/モデル設定\n"
            "- Search/Processing: web-search-mcp と container-use で証拠収集\n"
            "- LLM: Ollama 経由で暫定回答を生成し、検証ループへ連携\n"
            "- Verification: 主張抽出と追加検索で事実確認"
        )
    return (
        "- Input node normalized the query and language/model settings\n"
        "- Search + processing collected evidence via web-search-mcp/container-use\n"
        "- LLM node synthesized a provisional answer with tracked citations\n"
        "- Verification node extracted claims and cross-checked supporting snippets"
    )


def _render_verification_section(language: str, summary: Dict[str, Any], loops: int) -> str:
    average_confidence = summary.get("average_confidence")
    needs_additional = summary.get("needs_additional_search")
    passed = summary.get("passed")
    total = summary.get("total_claims")

    if language == "ja":
        lines = [
            f"- 検証ループ回数: {loops}",
            f"- 平均信頼度: {average_confidence:.2f}" if average_confidence is not None else "- 平均信頼度: N/A",
            f"- 主張確認: {passed}/{total} 件" if total is not None else "- 主張確認: N/A",
            f"- 追加調査: {'必要' if needs_additional else '不要'}",
        ]
    else:
        lines = [
            f"- Verification loops: {loops}",
            f"- Avg confidence: {average_confidence:.2f}" if average_confidence is not None else "- Avg confidence: N/A",
            f"- Claims validated: {passed}/{total}" if total is not None else "- Claims validated: N/A",
            f"- Additional research required: {'yes' if needs_additional else 'no'}",
        ]
    return "\n".join(lines)


def _generate_markdown_report(
    state: AgentState,
    sources_section: Dict[str, Any],
    language: str,
) -> Dict[str, Any]:
    provisional = state.get("provisional_answer", "").strip()
    query = state.get("query", "")
    verification_summary = state.get("verification_summary") or {}
    verification_loops = state.get("verification_count", 0)
    model_name = state.get("model_name", settings.default_model)
    timestamp = datetime.now(timezone.utc).isoformat()

    title = "調査レポート" if language == "ja" else "Research Report"
    summary_heading = "## 概要" if language == "ja" else "## Summary"
    methodology_heading = "## 調査方法" if language == "ja" else "## Methodology"
    sources_heading = "## 参照元" if language == "ja" else "## Sources"
    verification_heading = "## 検証状況" if language == "ja" else "## Verification Status"
    metadata_heading = "## メタデータ" if language == "ja" else "## Metadata"
    query_label = "### 調査テーマ" if language == "ja" else "### Research Question"

    methodology = _render_methodology(language)
    verification_block = _render_verification_section(language, verification_summary, verification_loops)

    lines = [
        f"# {title}",
        "",
        query_label,
        query or "(not provided)",
        "",
        summary_heading,
        provisional or "(provisional answer missing)",
        "",
        methodology_heading,
        methodology,
        "",
        sources_heading,
        sources_section["markdown"],
        "",
        verification_heading,
        verification_block,
        "",
        metadata_heading,
        f"- Generated: {timestamp}",
        f"- Model: {model_name}",
        f"- Language: {language}",
        f"- Sources cited: {len(sources_section['items'])}",
    ]

    return {
        "markdown": "\n".join(lines).strip() + "\n",
        "metadata": {
            "generated_at": timestamp,
            "model_name": model_name,
            "language": language,
            "verification_loops": verification_loops,
            "verification_summary": verification_summary,
            "sources": sources_section["items"],
        },
    }


def _write_pdf(pdf_path: Path, markdown_report: str) -> bool:
    if REPORTLAB_AVAILABLE:
        try:
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            width, height = A4
            text = c.beginText(40, height - 40)
            text.setFont("Helvetica", 11)
            for line in markdown_report.splitlines():
                text.textLine(line)
                if text.getY() <= 40:
                    c.drawText(text)
                    c.showPage()
                    text = c.beginText(40, height - 40)
                    text.setFont("Helvetica", 11)
            c.drawText(text)
            c.save()
            return True
        except Exception as exc:  # pragma: no cover - best effort
            logger.warning("ReportNode: Failed to write PDF via reportlab: %s", exc)

    try:
        pdf_path.write_text(
            "PDF generation unavailable. Install 'reportlab' to enable full export.\n\n"
            + markdown_report,
            encoding="utf-8",
        )
        return False
    except OSError as exc:  # pragma: no cover - best effort
        logger.warning("ReportNode: Failed to write PDF placeholder: %s", exc)
        return False


def _persist_markdown(history_path: str, report_content: str) -> Optional[Path]:
    if not history_path:
        return None
    session_path = Path(history_path)
    if not session_path.exists():
        return None

    session_id = session_path.name
    history_manager = HistoryManager(base_path=session_path.parent)
    try:
        history_manager.save_report(session_id, report_content, generate_pdf=False)
        return session_path / "report.md"
    except HistoryManagerError as exc:
        logger.warning("ReportNode: Failed to save report via HistoryManager: %s", exc)
        return None


def report_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate final report in Markdown (and optional PDF) format.

    The report consolidates the LLM provisional answer, verification summary,
    and deduplicated sources into a localized document saved under the session
    history path for CLI/verification consumption.
    """
    provisional = state.get("provisional_answer", "").strip()
    if not provisional:
        return add_error(state, "ReportNode: provisional_answer is empty")

    language = _normalize_language(state.get("language"))
    sources_section = format_sources(state.get("search_results") or [], state.get("processed_data") or [])
    report_bundle = _generate_markdown_report(state, sources_section, language)
    markdown_report = report_bundle["markdown"]

    history_path = state.get("history_path", "")
    report_path = _persist_markdown(history_path, markdown_report)

    existing_errors: List[str] = list(state.get("errors", []))  # type: ignore[arg-type]
    errors: List[str] = list(existing_errors)
    if history_path and report_path is None:
        errors = errors + ["ReportNode: Failed to persist Markdown report"]

    report_format = (state.get("report_format") or settings.report_format).lower()
    pdf_required = report_format in {"pdf", "both"}
    pdf_path: Optional[Path] = None
    pdf_ready = False

    if pdf_required and history_path:
        session_path = Path(history_path)
        if session_path.exists():
            pdf_path = session_path / "report.pdf"
            pdf_ready = _write_pdf(pdf_path, markdown_report)
        else:
            errors = errors + ["ReportNode: history_path does not exist, skipping PDF export"]

    update: Dict[str, Any] = {
        "final_report": markdown_report,
        "report_path": str(report_path) if report_path else "",
        "report_metadata": {
            **report_bundle["metadata"],
            "pdf_path": str(pdf_path) if pdf_path else "",
            "pdf_ready": pdf_ready,
        },
        "messages": [
            {
                "role": "assistant",
                "content": (
                    f"Report generated ({len(sources_section['items'])} sources, "
                    f"language={language}, pdf={'yes' if pdf_ready else 'no'})."
                ),
            }
        ],
    }

    if errors != existing_errors:
        update["errors"] = errors

    return update


__all__ = ["report_node"]
