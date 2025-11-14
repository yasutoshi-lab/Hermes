"""
Task command implementation.

Manages scheduled tasks for Hermes.
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
import logging
from hermes_cli.services import TaskService, ConfigService

console = Console()
logger = logging.getLogger(__name__)


def task_command(
    prompt: Optional[str] = typer.Option(None, "--prompt", help="Create new task with this prompt"),
    list_tasks: bool = typer.Option(False, "--list", help="List all tasks"),
    delete: Optional[str] = typer.Option(None, "--delete", help="Delete task by ID"),
    deleate: Optional[str] = typer.Option(None, "--deleate", help="Delete task by ID (typo alias)"),
):
    """
    Manage scheduled tasks.

    Examples:
        hermes task --prompt "Research quantum computing"
        hermes task --list
        hermes task --delete 2025-0001
    """
    try:
        task_service = TaskService()

        # Handle delete (support typo)
        delete_id = delete or deleate

        if delete_id:
            if task_service.delete_task(delete_id):
                console.print(f"[green]✓[/green] Task {delete_id} deleted")
            else:
                console.print(f"[red]✗[/red] Task {delete_id} not found")
                raise typer.Exit(code=1)

        elif list_tasks:
            tasks = task_service.list_tasks()

            if not tasks:
                console.print("[yellow]No tasks found[/yellow]")
                return

            # Create table
            table = Table(title="Scheduled Tasks")
            table.add_column("Task ID", style="cyan")
            table.add_column("Created", style="magenta")
            table.add_column("Status", style="yellow")
            table.add_column("Prompt", style="white")

            for task in tasks:
                table.add_row(
                    task.id,
                    task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    task.status,
                    task.prompt[:60] + "..." if len(task.prompt) > 60 else task.prompt
                )

            console.print(table)

        elif prompt:
            task = task_service.create_task(prompt)
            console.print(f"[green]✓[/green] Task created: {task.id}")
            console.print(f"Status: {task.status}")
            console.print(f"Prompt: {task.prompt}")

        else:
            console.print("[red]Error:[/red] Please specify --prompt, --list, or --delete")
            raise typer.Exit(code=2)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error(f"Task command failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
