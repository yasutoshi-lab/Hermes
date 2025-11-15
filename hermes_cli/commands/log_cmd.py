"""Log command for Hermes"""

import click
from pathlib import Path
from rich.console import Console

from hermes_cli.services.log_service import LogService

console = Console()


@click.command()
@click.option("--lines", "-n", type=int, default=50, help="表示行数")
@click.option("--follow", "-f", is_flag=True, help="リアルタイム表示")
@click.option("--task-id", type=str, help="特定タスクのログのみ表示")
@click.option("--debug", is_flag=True, help="デバッグログを表示")
@click.option(
    "--work-dir",
    type=click.Path(path_type=Path),
    help="ワークディレクトリパス",
)
def log(lines: int, follow: bool, task_id: str, debug: bool, work_dir: Path):
    """ログ表示"""

    service = LogService(work_dir)

    try:
        for line in service.read_logs(
            lines=lines, debug=debug, follow=follow, task_id=task_id
        ):
            console.print(line)
    except KeyboardInterrupt:
        console.print("\n[yellow]Log streaming stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Failed to read logs: {e}[/red]")
