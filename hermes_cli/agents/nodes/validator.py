"""Report validation node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState
from hermes_cli.tools.ollama_client import OllamaClient


async def validate_report(state: WorkflowState) -> WorkflowState:
    """レポート検証"""
    logger.info("Validating report", extra={"category": "RUN"})

    state["current_node"] = "validate_report"

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

        # 検証実行
        validation_result = await client.validate(
            report_text, state["original_prompt"]
        )

        state["validation_issues"] = validation_result.get("issues", [])
        state["additional_queries"] = validation_result.get("additional_queries", [])

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
