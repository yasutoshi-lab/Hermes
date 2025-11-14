"""
Queue command implementation.

Processes scheduled tasks sequentially until the queue is empty or a limit is met.
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
import logging

console = Console()
logger = logging.getLogger(__name__)


def queue_command(
    limit: int = typer.Option(
        1,
        "--limit",
        "-n",
        help="Maximum number of tasks to execute (<=0 means all)",
    ),
    run_all: bool = typer.Option(
        False,
        "--all",
        help="Process the entire queue regardless of --limit",
    ),
):
    """
    Execute scheduled tasks sequentially.

    Examples:
        hermes queue           # Run the oldest scheduled task
        hermes queue --all     # Drain the entire queue
        hermes queue -n 3      # Run three scheduled tasks
    """
    try:
        from hermes_cli.services import QueueService
    except ImportError:
        console.print("[red]Error:[/red] QueueService not yet implemented")
        raise typer.Exit(code=1)

    try:
        queue_service = QueueService()
        effective_limit: Optional[int]
        if run_all or limit <= 0:
            effective_limit = None
        else:
            effective_limit = limit

        results = queue_service.process_queue(limit=effective_limit)

        if not results:
            console.print("[yellow]No scheduled tasks to process[/yellow]")
            return

        table = Table(title="Queue Execution Summary")
        table.add_column("Task ID", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Report", style="magenta")
        table.add_column("Error", style="red")

        success_count = 0
        failure_count = 0

        for result in results:
            if result.status == "success":
                success_count += 1
                report_path = (
                    result.history_meta.report_file
                    if result.history_meta
                    else "(unknown)"
                )
                table.add_row(
                    result.task_id,
                    "[green]success[/green]",
                    report_path,
                    "",
                )
            else:
                failure_count += 1
                table.add_row(
                    result.task_id,
                    "[red]failed[/red]",
                    "",
                    result.error_message or "Unknown error",
                )

        console.print(table)
        console.print(
            f"[green]✓[/green] Completed queue run: "
            f"{success_count} succeeded, {failure_count} failed."
        )

    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        logger.error(f"Queue command failed: {exc}", exc_info=True)
        raise typer.Exit(code=1)
