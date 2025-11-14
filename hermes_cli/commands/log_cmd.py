"""
Log command implementation.

Views task execution logs.
"""

import typer
from rich.console import Console
from typing import Optional
import logging

from hermes_cli.services import TaskService

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
        resolved_task_id = task_id

        if not resolved_task_id:
            task_service = TaskService()
            latest_running = task_service.get_latest_running_task()
            if latest_running:
                resolved_task_id = latest_running.id
                console.print(f"[cyan]Defaulting to latest running task {resolved_task_id}[/cyan]")

        needle = f"task_id={resolved_task_id}" if resolved_task_id else None

        if follow:
            console.print("[cyan]Following log (Ctrl+C to exit)...[/cyan]\n")
            try:
                for line in log_service.stream():
                    if needle and needle not in line:
                        continue
                    console.print(line, end="")
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped[/yellow]")
        else:
            logs = log_service.tail(lines=lines)
            filtered_logs = [
                line for line in logs
                if not needle or needle in line
            ]
            if needle and not filtered_logs:
                console.print(f"[yellow]No log lines found for task {resolved_task_id}[/yellow]\n")
            for line in filtered_logs or logs:
                console.print(line, end="")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error(f"Log command failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
