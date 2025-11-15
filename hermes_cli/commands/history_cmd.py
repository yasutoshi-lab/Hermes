"""History command for Hermes"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from hermes_cli.services.history_service import HistoryService

console = Console()


@click.command()
@click.option("--limit", type=int, help="表示する履歴の最大件数")
@click.option("--export", type=str, help="エクスポート (TASK_ID:PATH)")
@click.option("--delete", type=str, help="履歴削除 (タスクID)")
@click.option(
    "--work-dir",
    type=click.Path(path_type=Path),
    help="ワークディレクトリパス",
)
def history(limit: int, export: str, delete: str, work_dir: Path):
    """実行履歴管理"""

    service = HistoryService(work_dir)

    if export:
        # エクスポート
        if ":" not in export:
            console.print("[red]✗ Export format: TASK_ID:PATH[/red]")
            return

        task_id, path = export.split(":", 1)
        if service.export_report(task_id, Path(path)):
            console.print(f"[green]✓ Report exported: {path}[/green]")
        else:
            console.print(f"[red]✗ Report not found: {task_id}[/red]")

    elif delete:
        # 削除
        if service.delete_history(delete):
            console.print(f"[green]✓ History deleted: {delete}[/green]")
        else:
            console.print(f"[red]✗ History not found: {delete}[/red]")

    else:
        # 一覧表示
        histories = service.list_histories(limit=limit)
        if not histories:
            console.print("[yellow]No history found[/yellow]")
            return

        table = Table(title="Execution History")
        table.add_column("Task ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Duration", style="yellow")
        table.add_column("Model", style="blue")
        table.add_column("Loops", style="green")
        table.add_column("Sources", style="white")
        table.add_column("Time", style="dim")

        for h in histories:
            status_color = "green" if h.status == "success" else "red"
            table.add_row(
                h.task_id,
                f"[{status_color}]{h.status}[/{status_color}]",
                f"{h.duration:.1f}s",
                h.model,
                str(h.loops),
                str(h.sources),
                h.start_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)
