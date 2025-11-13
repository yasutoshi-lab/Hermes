"""Hermes command-line interface."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from config import settings
from modules.history_manager import (
    HistoryManager,
    HistoryManagerError,
    SessionNotFoundError,
)
from modules.model_manager import ModelManager, OllamaConnectionError
from orchestrator.workflow import (
    WorkflowDependencies,
    WorkflowEvent,
    WorkflowRunResult,
    run_workflow,
)

console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unwrap_result(
    result: WorkflowRunResult | dict,
) -> Tuple[dict, List[WorkflowEvent]]:
    if isinstance(result, WorkflowRunResult):
        return result.final_state, result.events
    return result, []


def _render_events(events: List[WorkflowEvent]) -> None:
    if not events:
        return
    table = Table("Node", "Keys", title="Workflow Trace")
    for event in events:
        keys = ", ".join(event.payload.keys())
        table.add_row(event.node, keys or "-")
    console.print(table)


def _write_report_to_disk(final_state: dict, output_path: Optional[Path], output_format: str) -> None:
    if not output_path:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_text = final_state.get("final_report") or ""
    output_path.write_text(report_text, encoding="utf-8")
    console.print(f"[green]Saved report to {output_path}[/green]")

    metadata = final_state.get("report_metadata") or {}
    pdf_path = metadata.get("pdf_path")
    if output_format in {"pdf", "both"}:
        if pdf_path:
            console.print(f"[blue]PDF available at {pdf_path}[/blue]")
        else:
            console.print(
                "[yellow]PDF export was requested but is not available. "
                "Ensure report generation is configured for PDF output.[/yellow]"
            )


def _get_history_manager() -> HistoryManager:
    return HistoryManager(base_path=settings.session_storage_path)


def _get_model_manager() -> ModelManager:
    try:
        return ModelManager()
    except ImportError as exc:
        raise click.ClickException(
            "The 'ollama' package is required for model management. Install it to continue."
        ) from exc
    except OllamaConnectionError as exc:
        raise click.ClickException(str(exc)) from exc


def _display_errors(final_state: dict) -> None:
    errors = final_state.get("errors") or []
    if errors:
        for error in errors:
            console.print(f"[red]Error[/red]: {error}")


def _run_and_display(
    query: str,
    language: Optional[str],
    model_name: Optional[str],
    verbose: bool,
) -> Tuple[dict, List[WorkflowEvent]]:
    result = run_workflow(
        query=query,
        language=language,
        model_name=model_name,
        stream=verbose,
        dependencies=WorkflowDependencies(),
    )
    final_state, events = _unwrap_result(result)
    if verbose:
        _render_events(events)
    return final_state, events


# ---------------------------------------------------------------------------
# CLI definition
# ---------------------------------------------------------------------------

@click.group(help="Hermes - Local Research Analyst Agent")
@click.version_option()
def cli() -> None:
    """CLI entry point."""


@cli.command("query", help="Run a single-shot research query.")
@click.argument("query", nargs=1)
@click.option("--language", type=click.Choice(["ja", "en"]), default=None, help="Override language (default from settings).")
@click.option("--model", "model_name", default=None, help="Override LLM model name.")
@click.option("--output", type=click.Path(path_type=Path), default=None, help="Optional output path for Markdown report.")
@click.option("--format", "output_format", type=click.Choice(["markdown", "pdf", "both"]), default="markdown", show_default=True)
@click.option("--verbose", is_flag=True, help="Stream node progress.")
def query_command(
    query: str,
    language: Optional[str],
    model_name: Optional[str],
    output: Optional[Path],
    output_format: str,
    verbose: bool,
) -> None:
    try:
        final_state, events = _run_and_display(query, language, model_name, verbose)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    _display_errors(final_state)
    if output:
        _write_report_to_disk(final_state, output, output_format)

    report_path = final_state.get("report_path")
    if report_path:
        console.print(f"[green]Report stored at {report_path}[/green]")
    else:
        console.print("[yellow]Report path unavailable; history may be disabled.[/yellow]")


@cli.command("interactive", help="Start an interactive research session.")
@click.option("--language", type=click.Choice(["ja", "en"]), default=None, help="Override language (default from settings).")
@click.option("--model", "model_name", default=None, help="Override LLM model name.")
def interactive_command(language: Optional[str], model_name: Optional[str]) -> None:
    console.print("[bold blue]Hermes Interactive Mode[/bold blue]")
    console.print("Type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            query = Prompt.ask("[green]Query[/green]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Exiting interactive mode.[/yellow]")
            break

        if query.lower() in {"exit", "quit", "q"}:
            console.print("[yellow]Goodbye![/yellow]")
            break
        if not query:
            continue

        final_state, _ = _run_and_display(query, language, model_name, verbose=False)
        _display_errors(final_state)
        console.print(final_state.get("final_report", "").strip() or "[yellow]No report generated.[/yellow]")


# ---------------------------------------------------------------------------
# History Commands
# ---------------------------------------------------------------------------

@cli.group("history", help="Inspect or clean session history.")
def history_group() -> None:
    """History command group."""


@history_group.command("list", help="List recorded sessions.")
@click.option("--limit", type=int, default=10, show_default=True, help="Maximum number of sessions to show.")
def history_list(limit: int) -> None:
    manager = _get_history_manager()
    try:
        sessions = manager.list_sessions()[:limit]
    except HistoryManagerError as exc:
        raise click.ClickException(str(exc)) from exc

    if not sessions:
        console.print("[yellow]No sessions recorded yet.[/yellow]")
        return

    table = Table("Session ID")
    for session_id in sessions:
        table.add_row(session_id)
    console.print(table)


@history_group.command("show", help="Display a session artifact.")
@click.argument("session_id")
@click.option(
    "--section",
    type=click.Choice(["report", "search_results", "processed_data", "input", "state"]),
    default="report",
    show_default=True,
)
def history_show(session_id: str, section: str) -> None:
    manager = _get_history_manager()
    try:
        data = manager.load_session(session_id)
    except SessionNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except HistoryManagerError as exc:
        raise click.ClickException(str(exc)) from exc

    section_map = {
        "report": data.get("report"),
        "search_results": data.get("search_results"),
        "processed_data": data.get("processed_data"),
        "input": data.get("input"),
        "state": data.get("state"),
    }
    content = section_map.get(section)
    if not content:
        console.print(f"[yellow]Section '{section}' is empty for {session_id}.[/yellow]")
        return

    if isinstance(content, dict):
        console.print_json(data=content)
    else:
        console.print(content)


@history_group.command("cleanup", help="Delete sessions.")
@click.option("--session-id", help="Delete a specific session.")
@click.option("--keep-last", type=int, default=None, help="Keep the latest N sessions, delete the rest.")
def history_cleanup(session_id: Optional[str], keep_last: Optional[int]) -> None:
    manager = _get_history_manager()
    if session_id:
        try:
            manager.delete_session(session_id)
            console.print(f"[green]Deleted session {session_id}[/green]")
        except SessionNotFoundError as exc:
            raise click.ClickException(str(exc)) from exc
        except HistoryManagerError as exc:
            raise click.ClickException(str(exc)) from exc
        return

    if keep_last is not None:
        try:
            deleted = manager.cleanup_old_sessions(keep_last)
        except HistoryManagerError as exc:
            raise click.ClickException(str(exc)) from exc
        console.print(f"[green]Deleted {deleted} old session(s).[/green]")
        return

    raise click.ClickException("Provide either --session-id or --keep-last.")


# ---------------------------------------------------------------------------
# Model Commands
# ---------------------------------------------------------------------------

@cli.group("models", help="Manage Ollama models.")
def models_group() -> None:
    """Model command group."""


@models_group.command("list", help="List locally available models.")
def models_list() -> None:
    manager = _get_model_manager()
    try:
        models = manager.list_models()
    except OllamaConnectionError as exc:
        raise click.ClickException(str(exc)) from exc

    if not models:
        console.print("[yellow]No models available. Use 'hermes models pull <name>'.[/yellow]")
        return

    table = Table("Model")
    for model in models:
        table.add_row(model)
    console.print(table)


@models_group.command("info", help="Show model availability.")
@click.argument("model_name")
def models_info(model_name: str) -> None:
    manager = _get_model_manager()
    available = manager.is_model_available(model_name)
    if available:
        console.print(f"[green]{model_name} is available locally.[/green]")
    else:
        console.print(f"[yellow]{model_name} is not available. Use 'hermes models pull {model_name}'.[/yellow]")


@models_group.command("pull", help="Download a model via Ollama.")
@click.argument("model_name")
def models_pull(model_name: str) -> None:
    manager = _get_model_manager()
    try:
        manager.pull_model(model_name)
    except OllamaConnectionError as exc:
        raise click.ClickException(str(exc)) from exc
    console.print(f"[green]Model {model_name} downloaded.[/green]")


def main() -> None:
    """Console script entry point."""
    try:
        cli(prog_name="hermes")
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    main()
