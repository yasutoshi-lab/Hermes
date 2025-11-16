"""Final report generation node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState
from hermes_cli.tools.ollama_client import OllamaClient


async def finalize_report(state: WorkflowState) -> WorkflowState:
    """最終レポート生成"""
    logger.info("Finalizing report", extra={"category": "RUN"})

    state["current_node"] = "finalize_report"

    try:
        # ドラフトレポートを最終レポートとして保存
        draft = state.get("draft_report", {})
        state["final_report"] = draft

        # 関連性チェック
        config = state["config"]
        ollama_config = config.get("ollama", {})

        client = OllamaClient(
            api_url=ollama_config.get("api_url", "http://localhost:11434/api/chat"),
            model=ollama_config.get("model", "gpt-oss:20b"),
            timeout=ollama_config.get("timeout", 120),
            retry=ollama_config.get("retry", 3),
        )

        # レポート内容を取得
        report_content = draft.get("sections", [{}])[0].get("content", "")

        # 関連性をチェック
        relevance = await client.check_relevance(
            report_content=report_content,
            original_query=state["original_prompt"]
        )

        # メタデータに関連性情報を追加
        if "metadata" not in state["final_report"]:
            state["final_report"]["metadata"] = {}

        state["final_report"]["metadata"]["relevance_score"] = relevance.get("score", 0.0)
        state["final_report"]["metadata"]["relevance_reason"] = relevance.get("reason", "")

        # 低い関連性スコアの場合は警告
        if relevance.get("score", 0.0) < 0.5:
            logger.error(
                f"Report relevance too low: {relevance.get('score')} - {relevance.get('reason')}",
                extra={"category": "RUN"}
            )
            if "warnings" not in state["final_report"]["metadata"]:
                state["final_report"]["metadata"]["warnings"] = []
            state["final_report"]["metadata"]["warnings"].append(
                f"Low relevance score: {relevance.get('score'):.2f} - {relevance.get('reason')}"
            )
        else:
            logger.info(
                f"Report relevance check passed: {relevance.get('score'):.2f}",
                extra={"category": "RUN"}
            )

        await client.close()
        logger.info("Final report created", extra={"category": "RUN"})

    except Exception as e:
        logger.error(f"Report finalization failed: {e}", extra={"category": "RUN"})
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({"node": "finalize_report", "error": str(e)})
        raise

    return state
