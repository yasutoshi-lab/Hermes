"""Command-line interface for Hermes Research Agent."""

import sys
from typing import Optional
import click
from rich.console import Console
from rich.prompt import Prompt
from ..config import settings


console = Console()


@click.command()
@click.option(
    '--model',
    default=None,
    help=f'Ollama model to use (default: {settings.default_model})'
)
@click.option(
    '--language',
    type=click.Choice(['ja', 'en']),
    default=None,
    help=f'Interface language (default: {settings.default_language})'
)
@click.option(
    '--interactive/--no-interactive',
    default=True,
    help='Run in interactive mode'
)
@click.argument('query', required=False)
def main(
    model: Optional[str],
    language: Optional[str],
    interactive: bool,
    query: Optional[str]
):
    """
    Hermes - Local Research Analyst Agent.

    Run queries against local LLM with web search and verification.
    """
    console.print("[bold blue]Hermes Research Agent[/bold blue]", justify="center")
    console.print("Local AI-powered research assistant\n", justify="center")

    # TODO: Initialize workflow
    # TODO: Load configuration
    # TODO: Setup MCP connections

    if interactive:
        console.print("[yellow]Interactive mode. Type 'exit' or 'quit' to end.[/yellow]\n")
        while True:
            try:
                user_query = Prompt.ask("[bold green]Query[/bold green]")
                if user_query.lower() in ['exit', 'quit', 'q']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                # TODO: Process query through workflow
                console.print(f"[dim]Processing: {user_query}[/dim]")
                console.print("[red]Not implemented yet[/red]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    elif query:
        # Single query mode
        console.print(f"[dim]Processing query: {query}[/dim]\n")
        # TODO: Process single query
        console.print("[red]Not implemented yet[/red]")

    else:
        console.print("[red]Error: Please provide a query or use --interactive mode[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
