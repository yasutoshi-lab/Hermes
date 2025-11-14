"""
Hermes CLI Main Entry Point.

This module serves as the main entry point for the Hermes CLI application.
It initializes the Typer application and registers all commands.
"""

import typer
from hermes_cli.commands import (
    init_command,
    task_command,
    run_command,
    log_command,
    history_command,
    debug_command,
    queue_command,
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
app.command("queue")(queue_command)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version"),
):
    """Hermes CLI - Information Gathering Agent"""
    if version:
        from hermes_cli import __version__
        typer.echo(f"Hermes CLI version: {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
