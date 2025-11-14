"""
Log command implementation.

Views task execution logs.
"""

import typer
from rich.console import Console
from typing import Optional
import logging

console = Console()
logger = logging.getLogger(__name__)


def log_command(
    task_id: Optional[str] = typer.Option(None, "--task-id", help="Task ID to view logs for"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
):
    """
    View task execution logs.

    Examples:
        hermes log  # Show last 50 lines
        hermes log -n 100  # Show last 100 lines
        hermes log --follow  # Follow log in real-time
    """
    try:
        # NOTE: Requires LogService from phase3_task1_remaining_services
        try:
            from hermes_cli.services import LogService
        except ImportError:
            console.print("[red]Error:[/red] LogService not yet implemented")
            console.print("This feature requires completion of phase3_task1_remaining_services")
            raise typer.Exit(code=1)

        log_service = LogService()

        if task_id:
            console.print(f"[yellow]Note:[/yellow] Filtering by task ID not yet implemented")
            console.print(f"Showing all recent logs")

        if follow:
            console.print("[cyan]Following log (Ctrl+C to exit)...[/cyan]\n")
            try:
                for line in log_service.stream():
                    console.print(line, end="")
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped[/yellow]")
        else:
            logs = log_service.tail(lines=lines)
            for line in logs:
                console.print(line, end="")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error(f"Log command failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
