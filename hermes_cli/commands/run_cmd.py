"""Run command for Hermes"""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio

from hermes_cli.services.run_service import RunService
from hermes_cli.services.config_service import ConfigService

console = Console()


@click.command()
# コア
@click.option("--prompt", type=str, help="即時実行プロンプト")
@click.option("--task-id", type=str, help="実行するタスクID")
@click.option("--task-all", is_flag=True, help="全タスク実行")
@click.option("--export", type=click.Path(path_type=Path), help="レポート出力パス")
# LLM
@click.option("--api", type=str, help="Ollama APIエンドポイント")
@click.option("--model", type=str, help="LLMモデル名")
@click.option("--retry", type=int, help="リトライ回数")
# 検証
@click.option("--min-validation", type=int, help="最小検証ループ数")
@click.option("--max-validation", type=int, help="最大検証ループ数")
# 検索
@click.option("--min-search", type=int, help="最小ソース数")
@click.option("--max-search", type=int, help="最大ソース数")
@click.option("--query", type=int, help="クエリ生成数")
# 出力
@click.option(
    "--language", type=click.Choice(["ja", "en"]), help="出力言語"
)
# その他
@click.option("--work-dir", type=click.Path(path_type=Path), help="ワークディレクトリ")
def run(**kwargs):
    """リサーチタスク実行"""

    # 設定読み込み
    work_dir = kwargs.get("work_dir") or Path.home() / ".hermes"
    config_service = ConfigService(work_dir)

    try:
        config = config_service.load()
    except:
        console.print(
            "[red]✗ Config not found. Please run 'hermes init' first[/red]"
        )
        raise click.Abort()

    # CLIオプションマージ
    cli_args = {k: v for k, v in kwargs.items() if v is not None}
    config = ConfigService.merge_with_cli_args(config, cli_args)

    # サービス初期化
    run_service = RunService(config)

    # ロギング設定
    from hermes_cli.utils.logging import setup_logging

    setup_logging(config)

    # 実行
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running Hermes...", total=None)

        try:
            result = asyncio.run(
                run_service.execute(
                    prompt=kwargs.get("prompt"),
                    task_id=kwargs.get("task_id"),
                    task_all=kwargs.get("task_all", False),
                )
            )

            progress.update(task, completed=True)

            console.print("\n[green]✓ Execution completed![/green]")
            console.print(f"Report saved to: {result['report_path']}")

            if kwargs.get("export"):
                import shutil

                shutil.copy(result["report_path"], kwargs["export"])
                console.print(f"Exported to: {kwargs['export']}")

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"\n[red]✗ Execution failed: {e}[/red]")
            raise click.Abort()
