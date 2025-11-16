"""Report validation node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState
from hermes_cli.tools.ollama_client import OllamaClient
from hermes_cli.agents.nodes.query_generator import validate_query_quality


async def validate_report(state: WorkflowState) -> WorkflowState:
    """レポート検証"""
    logger.info("Validating report", extra={"category": "RUN"})

    state["current_node"] = "validate_report"

    # 検証ループカウンタを更新（Edge関数ではなくNode内で更新）
    if "validation_loop" not in state:
        state["validation_loop"] = 0
    state["validation_loop"] += 1

    try:
        config = state["config"]
        ollama_config = config.get("ollama", {})

        client = OllamaClient(
            api_url=ollama_config.get("api_url", "http://localhost:11434/api/chat"),
            model=ollama_config.get("model", "gpt-oss:20b"),
            timeout=ollama_config.get("timeout", 120),
            retry=ollama_config.get("retry", 3),
        )

        # ドラフトレポートをMarkdown化
        draft = state.get("draft_report", state.get("final_report", {}))
        report_text = draft.get("sections", [{}])[0].get("content", "")

        # 言語設定を取得
        language = config.get("language", "ja")

        # 検証設定を取得
        validation_config = config.get("validation", {})
        strictness = validation_config.get("strictness", "moderate")
        max_additional_queries = validation_config.get("max_additional_queries", 3)

        # 検証実行
        validation_result = await client.validate(
            report_text,
            state["original_prompt"],
            language=language,
            strictness=strictness,
            max_additional_queries=max_additional_queries
        )

        state["validation_issues"] = validation_result.get("issues", [])

        # 追加クエリの品質チェック
        raw_additional_queries = validation_result.get("additional_queries", [])
        validated_additional_queries = validate_query_quality(raw_additional_queries, language)

        # 品質チェックで除外されたクエリがある場合はログに記録
        if len(validated_additional_queries) < len(raw_additional_queries):
            logger.info(
                f"Filtered additional queries: {len(raw_additional_queries)} -> {len(validated_additional_queries)}",
                extra={"category": "RUN"}
            )

        state["additional_queries"] = validated_additional_queries

        logger.info(
            f"Validation completed: {len(state['validation_issues'])} issues found",
            extra={"category": "RUN"},
        )

        await client.close()

    except Exception as e:
        logger.error(f"Validation failed: {e}", extra={"category": "RUN"})
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({"node": "validate_report", "error": str(e)})
        # 検証失敗時はループを終了
        state["validation_issues"] = []
        state["additional_queries"] = []

    return state
