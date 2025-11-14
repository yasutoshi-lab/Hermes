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
    export: Optional[str] = typer.Option(None, "--export", help="Export format: TASK_ID:PATH"),
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
            try:
                task_id, path_str = export.split(":", 1)
                dest_path = Path(path_str)

                if history_service.export_report(task_id, dest_path):
                    console.print(f"[green]✓[/green] Report exported to {dest_path}")
                else:
                    console.print(f"[red]✗[/red] History {task_id} not found")
                    raise typer.Exit(code=1)

            except ValueError:
                console.print("[red]Error:[/red] Export format should be TASK_ID:PATH")
                console.print("Example: --export 2025-0001:./report.md")
                raise typer.Exit(code=2)

        else:
            # List history
            histories = history_service.list_history(limit=limit)

            if not histories:
                console.print("[yellow]No history found[/yellow]")
                return

            # Create table
            table = Table(title=f"Execution History (last {len(histories)})")
            table.add_column("Task ID", style="cyan")
            table.add_column("Created", style="magenta")
            table.add_column("Finished", style="magenta")
            table.add_column("Model", style="yellow")
            table.add_column("Loops", justify="right", style="green")
            table.add_column("Sources", justify="right", style="blue")

            for history in histories:
                duration = (history.finished_at - history.created_at).seconds
                table.add_row(
                    history.id,
                    history.created_at.strftime("%Y-%m-%d %H:%M"),
                    f"{history.finished_at.strftime('%H:%M')} ({duration}s)",
                    history.model,
                    str(history.validation_loops),
                    str(history.source_count),
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error(f"History command failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
