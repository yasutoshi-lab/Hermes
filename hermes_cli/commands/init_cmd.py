"""
Init command implementation.

Initializes Hermes data directories and configuration.
"""

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
