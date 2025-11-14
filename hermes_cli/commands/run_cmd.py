"""
Run command implementation.

Executes research tasks and manages execution options.
"""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from pathlib import Path
from typing import Optional
import logging
from hermes_cli.services import ConfigService

console = Console()
logger = logging.getLogger(__name__)


def run_command(
    prompt: Optional[str] = typer.Option(None, "--prompt", help="Research prompt"),
    export: Optional[Path] = typer.Option(None, "--export", help="Export report to path"),
    api: Optional[str] = typer.Option(None, "--api", help="Ollama API URL"),
    model: Optional[str] = typer.Option(None, "--model", help="Model name"),
    min_validation: Optional[int] = typer.Option(None, "--min-validation", help="Min validation loops"),
    max_validation: Optional[int] = typer.Option(None, "--max-validation", help="Max validation loops"),
    query: Optional[int] = typer.Option(None, "--query", help="Number of queries to generate"),
    language: Optional[str] = typer.Option(None, "--language", help="Output language (ja/en)"),
    retry: Optional[int] = typer.Option(None, "--retry", help="Ollama retry count"),
    min_search: Optional[int] = typer.Option(None, "--min-search", help="Min search sources"),
    max_search: Optional[int] = typer.Option(None, "--max-search", help="Max search sources"),
    clear: bool = typer.Option(False, "--clear", help="Reset config to default"),
):
    """
    Execute a research task.

    Examples:
        hermes run --prompt "Explain quantum computing"
        hermes run --prompt "AI trends" --language en --max-validation 5
        hermes run --export ./report.md  # Export last result
        hermes run --clear  # Reset configuration
    """
    try:
        if clear:
            config_service = ConfigService()
            config_service.reset_to_default()
            console.print("[green]✓[/green] Configuration reset to default")
            return

        if export:
            # Export most recent report
            # NOTE: Requires HistoryService from phase3_task1_remaining_services
            try:
                from hermes_cli.services import HistoryService
            except ImportError:
                console.print("[red]Error:[/red] HistoryService not yet implemented")
                console.print("This feature requires completion of phase3_task1_remaining_services")
                raise typer.Exit(code=1)

            history_service = HistoryService()
            histories = history_service.list_history(limit=1)

            if not histories:
                console.print("[red]✗[/red] No reports available")
                raise typer.Exit(code=1)

            if history_service.export_report(histories[0].id, export):
                console.print(f"[green]✓[/green] Report exported to {export}")
            else:
                console.print("[red]✗[/red] Export failed")
                raise typer.Exit(code=1)
            return

        if not prompt:
            console.print("[red]Error:[/red] Please provide --prompt")
            raise typer.Exit(code=2)

        # Build options dict
        options = {}
        if api:
            options['api'] = api
        if model:
            options['model'] = model
        if retry:
            options['retry'] = retry
        if language:
            options['language'] = language
        if min_validation is not None:
            options['min_validation'] = min_validation
        if max_validation is not None:
            options['max_validation'] = max_validation
        if query is not None:
            options['query_count'] = query
        if min_search is not None:
            options['min_sources'] = min_search
        if max_search is not None:
            options['max_sources'] = max_search

        # Execute task
        # NOTE: Requires RunService from phase2_task1_service_foundation
        try:
            from hermes_cli.services import RunService
        except ImportError:
            console.print("[red]Error:[/red] RunService not yet implemented")
            console.print("This feature requires completion of phase2_task1_service_foundation")
            raise typer.Exit(code=1)

        run_service = RunService()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Executing research task...", total=None)

            history_meta = run_service.run_prompt(prompt, options)

        # Display results
        console.print(Panel.fit(
            f"[green]✓[/green] Task completed successfully!\n\n"
            f"Task ID: {history_meta.id}\n"
            f"Model: {history_meta.model}\n"
            f"Sources: {history_meta.source_count}\n"
            f"Validation loops: {history_meta.validation_loops}\n"
            f"Duration: {(history_meta.finished_at - history_meta.created_at).seconds}s\n\n"
            f"Report: ~/.hermes/history/{history_meta.report_file}",
            title="Execution Complete",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error(f"Run command failed: {e}", exc_info=True)
        raise typer.Exit(code=3)
