"""依存サービス疎通テスト

このスクリプトは、Hermesが依存する外部サービスの接続性を確認します：
- Redis
- Ollama
- SearxNG
- Langfuse
"""

import asyncio
import sys
from typing import Dict, Any
import httpx
import redis
from rich.console import Console
from rich.table import Table
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from hermes_cli.models.config import HermesConfig
from hermes_cli.persistence.config_repository import ConfigRepository


console = Console()


class DependencyChecker:
    """依存サービスチェッカー"""

    def __init__(self, config: HermesConfig):
        self.config = config
        self.results: Dict[str, Dict[str, Any]] = {}

    async def check_redis(self) -> Dict[str, Any]:
        """Redis接続テスト"""
        try:
            client = redis.from_url(self.config.search.redis_url, decode_responses=True)

            # 接続テスト
            pong = client.ping()
            if not pong:
                raise Exception("PING failed")

            # 読み書きテスト
            test_key = "_hermes_test_key"
            test_value = "test_value"
            client.set(test_key, test_value, ex=10)
            retrieved = client.get(test_key)
            client.delete(test_key)

            if retrieved != test_value:
                raise Exception("Read/Write test failed")

            # 情報取得
            info = client.info()

            return {
                "status": "✓ OK",
                "version": info.get("redis_version", "unknown"),
                "details": f"Connected clients: {info.get('connected_clients', 0)}",
                "error": None,
            }
        except Exception as e:
            return {
                "status": "✗ FAILED",
                "version": "N/A",
                "details": str(e),
                "error": str(e),
            }

    async def check_ollama(self) -> Dict[str, Any]:
        """Ollama接続テスト"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # ヘルスチェック
                api_base = self.config.ollama.api_url.replace("/api/chat", "")
                response = await client.get(f"{api_base}/api/tags")

                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")

                data = response.json()
                models = data.get("models", [])

                # 設定されたモデルが利用可能か確認
                model_names = [m.get("name") for m in models]
                configured_model = self.config.ollama.model
                model_available = configured_model in model_names

                return {
                    "status": "✓ OK" if model_available else "⚠ WARNING",
                    "version": f"{len(models)} models available",
                    "details": f"Configured: {configured_model}, Available: {model_available}",
                    "error": None if model_available else f"Model '{configured_model}' not found",
                }
        except Exception as e:
            return {
                "status": "✗ FAILED",
                "version": "N/A",
                "details": str(e),
                "error": str(e),
            }

    async def check_searxng(self) -> Dict[str, Any]:
        """SearxNG接続テスト"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # ヘルスチェック
                response = await client.get(
                    f"{self.config.search.searxng_base_url}/search",
                    params={"q": "test", "format": "json"},
                    headers={
                        "X-Forwarded-For": "127.0.0.1",
                        "X-Real-IP": "127.0.0.1",
                        "User-Agent": "Hermes/1.0 (Test Agent)",
                    },
                )

                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")

                data = response.json()
                results_count = len(data.get("results", []))

                return {
                    "status": "✓ OK",
                    "version": "SearxNG",
                    "details": f"Test search returned {results_count} results",
                    "error": None,
                }
        except Exception as e:
            return {
                "status": "✗ FAILED",
                "version": "N/A",
                "details": str(e),
                "error": str(e),
            }

    async def check_langfuse(self) -> Dict[str, Any]:
        """Langfuse接続テスト"""
        if not self.config.langfuse.enabled:
            return {
                "status": "○ DISABLED",
                "version": "N/A",
                "details": "Langfuse is disabled in config",
                "error": None,
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # ヘルスチェック
                response = await client.get(
                    f"{self.config.langfuse.host}/api/public/health"
                )

                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")

                data = response.json()

                return {
                    "status": "✓ OK",
                    "version": data.get("version", "unknown"),
                    "details": f"Status: {data.get('status', 'unknown')}",
                    "error": None,
                }
        except Exception as e:
            return {
                "status": "✗ FAILED",
                "version": "N/A",
                "details": str(e),
                "error": str(e),
            }

    async def check_all(self) -> Dict[str, Dict[str, Any]]:
        """全依存サービスをチェック"""
        console.print("\n[bold cyan]Checking Hermes Dependencies...[/bold cyan]\n")

        # 並列実行
        results = await asyncio.gather(
            self.check_redis(),
            self.check_ollama(),
            self.check_searxng(),
            self.check_langfuse(),
        )

        self.results = {
            "Redis": results[0],
            "Ollama": results[1],
            "SearxNG": results[2],
            "Langfuse": results[3],
        }

        return self.results

    def display_results(self):
        """結果を表形式で表示"""
        table = Table(title="Dependency Check Results")

        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Version/Info", style="magenta")
        table.add_column("Details", style="green")

        for service, result in self.results.items():
            status_style = (
                "green" if result["status"].startswith("✓")
                else "yellow" if result["status"].startswith("⚠") or result["status"].startswith("○")
                else "red"
            )

            table.add_row(
                service,
                f"[{status_style}]{result['status']}[/{status_style}]",
                result["version"],
                result["details"],
            )

        console.print(table)

        # サマリー
        failed = sum(1 for r in self.results.values() if r["status"].startswith("✗"))
        warning = sum(1 for r in self.results.values() if r["status"].startswith("⚠"))

        console.print()
        if failed > 0:
            console.print(f"[bold red]✗ {failed} service(s) failed[/bold red]")
            return False
        elif warning > 0:
            console.print(f"[bold yellow]⚠ {warning} warning(s)[/bold yellow]")
            return True
        else:
            console.print("[bold green]✓ All services are healthy[/bold green]")
            return True


async def main():
    """メインエントリーポイント"""
    try:
        # 設定読み込み
        config_repo = ConfigRepository()
        config = config_repo.load()

        console.print(f"[dim]Config loaded from: {config.work_dir}/config.yaml[/dim]")

        # 依存チェック実行
        checker = DependencyChecker(config)
        await checker.check_all()
        checker.display_results()

        # 終了コード
        success = not any(r["status"].startswith("✗") for r in checker.results.values())
        sys.exit(0 if success else 1)

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
