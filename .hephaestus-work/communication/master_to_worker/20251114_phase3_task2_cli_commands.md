# Task: CLI Commands Implementation

**Task ID**: phase3_task2_cli_commands
**Priority**: high
**Assigned to**: worker-3
**Dependencies**: phase2_task1_service_foundation, phase3_task1_remaining_services

## Objective
Implement all CLI command modules for Hermes: init, task, run, log, history, and debug. These commands provide the user interface to all Hermes functionality.

## Context
CLI commands are the user-facing interface. They use Typer for argument parsing and services for business logic. Commands should provide clear output, proper error messages, and follow Unix CLI conventions.

Reference design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (section 7)

## Requirements

### 1. Implement `commands/init_cmd.py`

```python
import typer
from rich.console import Console
from rich.panel import Panel
import logging
from hermes_cli.services import ConfigService
from hermes_cli.persistence.file_paths import FilePaths

console = Console()
logger = logging.getLogger(__name__)


def init_command():
    """
    Initialize Hermes data directories and configuration.

    Creates ~/.hermes/ directory structure and default config.yaml if not exists.
    """
    try:
        file_paths = FilePaths()

        # Check if already initialized
        if file_paths.base.exists() and file_paths.config_file.exists():
            console.print("[yellow]Hermes is already initialized.[/yellow]")
            console.print(f"Location: {file_paths.base}")
            return

        # Create directories
        file_paths.ensure_directories()

        # Create default config if needed
        config_service = ConfigService(file_paths)
        config = config_service.load()  # This will create default if missing

        # Success message
        console.print(Panel.fit(
            f"[green]✓[/green] Hermes initialized successfully!\n\n"
            f"Data directory: {file_paths.base}\n"
            f"Config file: {file_paths.config_file}\n\n"
            f"You can now use: hermes run --prompt \"your query\"",
            title="Initialization Complete",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error(f"Init command failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
```

### 2. Implement `commands/task_cmd.py`

```python
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
```

### 3. Implement `commands/run_cmd.py`

```python
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from pathlib import Path
from typing import Optional
import logging
from hermes_cli.services import RunService, ConfigService

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
            from hermes_cli.services import HistoryService
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
```

### 4. Implement `commands/log_cmd.py`

```python
import typer
from rich.console import Console
import logging
from hermes_cli.services import LogService, TaskService

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
```

### 5. Implement `commands/history_cmd.py`

```python
import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional
import logging
from hermes_cli.services import HistoryService

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
```

### 6. Implement `commands/debug_cmd.py`

```python
import typer
from rich.console import Console
import logging
from hermes_cli.services import DebugService

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
```

### 7. Update `commands/__init__.py`

```python
"""
CLI commands for Hermes.

Each module implements a specific command group:
- init: Initialize Hermes environment
- task: Task scheduling and management
- run: Execute research tasks
- log: View execution logs
- history: Manage execution history
- debug: View debug logs
"""

from .init_cmd import init_command
from .task_cmd import task_command
from .run_cmd import run_command
from .log_cmd import log_command
from .history_cmd import history_command
from .debug_cmd import debug_command

__all__ = [
    "init_command",
    "task_command",
    "run_command",
    "log_command",
    "history_command",
    "debug_command",
]
```

### 8. Update `main.py` to Register Commands

```python
import typer
from hermes_cli.commands import (
    init_command,
    task_command,
    run_command,
    log_command,
    history_command,
    debug_command,
)

app = typer.Typer(
    name="hermes",
    help="Hermes - CLI Research Agent",
    add_completion=False,
)

# Register commands
app.command("init")(init_command)
app.command("task")(task_command)
app.command("run")(run_command)
app.command("log")(log_command)
app.command("history")(history_command)
app.command("debug")(debug_command)


@app.callback()
def callback(
    version: bool = typer.Option(False, "--version", help="Show version"),
):
    """Hermes CLI - Information Gathering Agent"""
    if version:
        from hermes_cli import __version__
        typer.echo(f"Hermes CLI version: {__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app()
```

## Implementation Notes

### CLI Design Principles
- Use Rich library for beautiful output
- Provide clear error messages
- Support common typos (--deleate)
- Follow Unix conventions (exit codes, --help)
- Show progress for long operations

### Exit Codes
- 0: Success
- 1: General error
- 2: User input error
- 3: External tool error

### Output Formatting
- Use Rich Console for colored output
- Use Tables for list displays
- Use Panels for important messages
- Use Progress bars for long operations

### Error Handling
- Catch exceptions and display user-friendly messages
- Log detailed errors for debugging
- Use appropriate exit codes

## Expected Output

All files in `/home/ubuntu/python_project/Hermes/hermes_cli/`:
1. `commands/init_cmd.py`
2. `commands/task_cmd.py`
3. `commands/run_cmd.py`
4. `commands/log_cmd.py`
5. `commands/history_cmd.py`
6. `commands/debug_cmd.py`
7. Updated `commands/__init__.py`
8. Updated `main.py` with command registration

## Resources

- Design document section: 7 (all subsections)
- Typer documentation: https://typer.tiangolo.com/
- Rich documentation: https://rich.readthedocs.io/

## Success Criteria

- All 6 commands implemented
- Main.py properly registers all commands
- Rich output formatting works correctly
- Error handling and exit codes correct
- Can run: `python -m hermes_cli.main --help`
- Can run: `python -m hermes_cli.main init`
- All commands show proper help text
- Integration with services layer working
