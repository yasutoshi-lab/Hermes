"""Task command for Hermes"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from hermes_cli.services.task_service import TaskService

console = Console()


@click.command()
@click.option("--add", type=str, help="新しいタスクを追加")
@click.option("--list", "list_tasks", is_flag=True, help="タスク一覧を表示")
@click.option("--remove", type=str, help="タスクを削除 (タスクID指定)")
@click.option(
    "--work-dir",
    type=click.Path(path_type=Path),
    help="ワークディレクトリパス",
)
def task(add: str, list_tasks: bool, remove: str, work_dir: Path):
    """タスク管理"""

    service = TaskService(work_dir)

    if add:
        # タスク追加
        new_task = service.create_task(add)
        console.print(f"[green]✓ Task created: {new_task.id}[/green]")
        console.print(f"Prompt: {new_task.prompt}")

    elif list_tasks:
        # タスク一覧
        tasks = service.list_tasks()
        if not tasks:
            console.print("[yellow]No tasks found[/yellow]")
            return

        table = Table(title="Tasks")
        table.add_column("ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Prompt", style="white")
        table.add_column("Created", style="green")

        for t in tasks:
            table.add_row(
                t.id,
                t.status,
                t.prompt[:50] + "..." if len(t.prompt) > 50 else t.prompt,
                t.created_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)

    elif remove:
        # タスク削除
        if service.delete_task(remove):
            console.print(f"[green]✓ Task deleted: {remove}[/green]")
        else:
            console.print(f"[red]✗ Task not found: {remove}[/red]")

    else:
        console.print("[yellow]Please specify --add, --list, or --remove[/yellow]")
