"""
History command implementation.

Manages execution history and report exports.
"""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional
import logging

console = Console()
logger = logging.getLogger(__name__)


def history_command(
    export: Optional[str] = typer.Option(
        None,
        "--export",
        help="Export report: TASK_ID:PATH (e.g., 2025-0001:./report.md)",
    ),
    delete: Optional[str] = typer.Option(None, "--delete", help="Delete history by ID"),
    deleate: Optional[str] = typer.Option(None, "--deleate", help="Delete history by ID (typo alias)"),
    limit: int = typer.Option(100, "--limit", help="Max entries to show"),
):
    """
    Manage execution history.

    Examples:
        hermes history  # List all history
        hermes history --limit 10  # Show last 10
        hermes history --export 2025-0001:./report.md  # Export report
        hermes history --delete 2025-0001  # Delete history
    """
    try:
        # NOTE: Requires HistoryService from phase3_task1_remaining_services
        try:
            from hermes_cli.services import HistoryService
        except ImportError:
            console.print("[red]Error:[/red] HistoryService not yet implemented")
            console.print("This feature requires completion of phase3_task1_remaining_services")
            raise typer.Exit(code=1)

        history_service = HistoryService()

        # Handle delete (support typo)
        delete_id = delete or deleate

        if delete_id:
            if history_service.delete_history(delete_id):
                console.print(f"[green]✓[/green] History {delete_id} deleted")
            else:
                console.print(f"[red]✗[/red] History {delete_id} not found")
                raise typer.Exit(code=1)

        elif export:
            # Parse TASK_ID:PATH format
            if ":" not in export:
                console.print("[red]✗[/red] Export format must be TASK_ID:PATH (e.g., 2025-0001:./report.md)")
                raise typer.Exit(code=1)
            task_id, dest_path_str = export.split(":", 1)
            dest_path = Path(dest_path_str)
            meta = history_service.get_history(task_id)
            if not meta:
                console.print(f"[red]✗[/red] History {task_id} not found")
                raise typer.Exit(code=1)

            if meta.status != "success":
                console.print(f"[red]✗[/red] History {task_id} failed; no report to export")
                if meta.error_message:
                    console.print(f"Reason: {meta.error_message}")
                raise typer.Exit(code=1)

            if history_service.export_report(task_id, dest_path):
                console.print(f"[green]✓[/green] Report exported to {dest_path}")
            else:
                console.print(f"[red]✗[/red] Failed to export report for {task_id}")
                raise typer.Exit(code=1)

        else:
            # List history
            histories = history_service.list_history(limit=limit)

            if not histories:
                console.print("[yellow]No history found[/yellow]")
                return

            # Create table
            table = Table(title=f"Execution History (last {len(histories)})")
            table.add_column("Task ID", style="cyan")
            table.add_column("Status", style="yellow")
            table.add_column("Created", style="magenta")
            table.add_column("Finished", style="magenta")
            table.add_column("Model", style="yellow")
            table.add_column("Loops", justify="right", style="green")
            table.add_column("Sources", justify="right", style="blue")
            table.add_column("Error", style="red")

            for history in histories:
                duration = (history.finished_at - history.created_at).seconds
                status_label = (
                    "[green]success[/green]" if history.status == "success"
                    else "[red]failed[/red]"
                )
                error_display = ""
                if history.error_message:
                    error_display = history.error_message if len(history.error_message) <= 60 else history.error_message[:57] + "..."
                table.add_row(
                    history.id,
                    status_label,
                    history.created_at.strftime("%Y-%m-%d %H:%M"),
                    f"{history.finished_at.strftime('%H:%M')} ({duration}s)",
                    history.model,
                    str(history.validation_loops),
                    str(history.source_count),
                    error_display,
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error(f"History command failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
