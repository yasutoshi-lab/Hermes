"""Query generation node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState
from hermes_cli.tools.ollama_client import OllamaClient
from typing import List


def validate_query_quality(queries: List[str], language: str) -> List[str]:
    """生成されたクエリの品質をチェック"""
    validated_queries = []

    for query in queries:
        # 長すぎるクエリを除外（検索結果が0件になりやすい）
        if len(query) > 150:
            logger.warning(
                f"Query too specific, skipping: {query[:50]}...",
                extra={"category": "QUERY"}
            )
            continue

        # 短すぎるクエリを除外（ノイズが多い）
        if len(query) < 5:
            logger.warning(
                f"Query too short, skipping: {query}",
                extra={"category": "QUERY"}
            )
            continue

        # 言語チェック（日本語クエリなら日本語文字を含むべき）
        if language == "ja":
            has_japanese = any('\u3000' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff' for c in query)
            if not has_japanese:
                logger.warning(
                    f"Query language mismatch (expected Japanese), skipping: {query}",
                    extra={"category": "QUERY"}
                )
                continue

        validated_queries.append(query)

    return validated_queries


async def generate_queries(state: WorkflowState) -> WorkflowState:
    """検索クエリ生成"""
    logger.info("Generating queries", extra={"category": "RUN"})

    state["current_node"] = "generate_queries"

    try:
        config = state["config"]
        ollama_config = config.get("ollama", {})

        client = OllamaClient(
            api_url=ollama_config.get("api_url", "http://localhost:11434/api/chat"),
            model=ollama_config.get("model", "gpt-oss:20b"),
            timeout=ollama_config.get("timeout", 120),
            retry=ollama_config.get("retry", 3),
        )

        num_queries = config.get("search", {}).get("query_count", 3)
        language = config.get("language", "ja")

        # クエリ生成
        raw_queries = await client.generate_queries(state["normalized_prompt"], num_queries)

        # クエリ品質チェック
        queries = validate_query_quality(raw_queries, language)

        # 品質チェックで全て除外された場合は元のクエリを使用
        if not queries and raw_queries:
            logger.warning(
                "All queries filtered out, using original queries",
                extra={"category": "RUN"}
            )
            queries = raw_queries

        state["queries"] = queries

        logger.info(
            f"Generated {len(queries)} queries (from {len(raw_queries)} raw queries)",
            extra={"category": "RUN", "queries": queries},
        )

        await client.close()

    except Exception as e:
        logger.error(f"Query generation failed: {e}", extra={"category": "RUN"})
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({"node": "generate_queries", "error": str(e)})
        raise

    return state
