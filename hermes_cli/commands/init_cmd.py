"""Init command for Hermes"""

import click
from pathlib import Path
from rich.console import Console
import shutil

from hermes_cli.models.config import HermesConfig
from hermes_cli.persistence.config_repository import ConfigRepository
from hermes_cli.persistence.file_paths import FilePaths

console = Console()


@click.command()
@click.option(
    "--work-dir",
    type=click.Path(path_type=Path),
    default=Path.home() / ".hermes",
    help="ワークディレクトリパス",
)
@click.option("--clear", is_flag=True, help="既存設定を削除して再初期化")
def init(work_dir: Path, clear: bool):
    """Hermesワークスペース初期化"""

    if work_dir.exists() and not clear:
        console.print(
            f"[yellow]Hermes is already initialized at {work_dir}[/yellow]"
        )
        console.print("Use --clear to reinitialize")
        return

    if clear and work_dir.exists():
        console.print(f"[yellow]Clearing existing workspace...[/yellow]")
        shutil.rmtree(work_dir)

    # ディレクトリ作成
    console.print(f"[blue]Initializing Hermes workspace at {work_dir}[/blue]")

    file_paths = FilePaths(work_dir)
    file_paths.ensure_directories()

    console.print(f"  ✓ Created cache/")
    console.print(f"  ✓ Created task/")
    console.print(f"  ✓ Created log/")
    console.print(f"  ✓ Created debug_log/")
    console.print(f"  ✓ Created history/")
    console.print(f"  ✓ Created searxng/")

    # デフォルト設定保存
    config = HermesConfig(work_dir=work_dir)
    repository = ConfigRepository(work_dir)
    repository.save(config)
    console.print(f"  ✓ Created config.yaml")

    # docker-compose.yaml テンプレートコピー
    template_src = Path(__file__).parent.parent.parent / ".hermes_template" / "docker-compose.yaml"
    if template_src.exists():
        shutil.copy(template_src, file_paths.docker_compose_file)
        console.print(f"  ✓ Created docker-compose.yaml")

    console.print("\n[green]✓ Hermes initialized successfully![/green]")
    console.print("\nNext steps:")
    console.print(f"  1. cd {work_dir}")
    console.print("  2. docker compose up -d")
    console.print('  3. hermes run --prompt "Your research question"')
