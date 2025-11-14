"""
Debug command implementation.

Views debug logs with filtering by log level.
"""

import typer
from rich.console import Console
import logging

console = Console()
logger = logging.getLogger(__name__)


def debug_command(
    info: bool = typer.Option(False, "--info", help="Show only INFO level"),
    warning: bool = typer.Option(False, "--warning", help="Show only WARNING level"),
    error: bool = typer.Option(False, "--error", help="Show only ERROR level"),
    all_levels: bool = typer.Option(False, "--all", help="Show all levels"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow output"),
):
    """
    View debug logs with filtering.

    Examples:
        hermes debug  # Show all logs
        hermes debug --error  # Show only errors
        hermes debug --follow  # Follow logs in real-time
    """
    try:
        # NOTE: Requires DebugService from phase3_task1_remaining_services
        try:
            from hermes_cli.services import DebugService
        except ImportError:
            console.print("[red]Error:[/red] DebugService not yet implemented")
            console.print("This feature requires completion of phase3_task1_remaining_services")
            raise typer.Exit(code=1)

        debug_service = DebugService()

        # Determine level
        if error:
            level = "error"
        elif warning:
            level = "warning"
        elif info:
            level = "info"
        else:
            level = "all"

        if follow:
            console.print(f"[cyan]Following debug logs [level={level}] (Ctrl+C to exit)...[/cyan]\n")
            try:
                for line in debug_service.stream(level=level):
                    console.print(line, end="")
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped[/yellow]")
        else:
            logs = debug_service.tail(lines=lines, level=level)
            for line in logs:
                console.print(line, end="")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error(f"Debug command failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
