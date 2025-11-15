"""Final report generation node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState


def finalize_report(state: WorkflowState) -> WorkflowState:
    """最終レポート生成"""
    logger.info("Finalizing report", extra={"category": "RUN"})

    state["current_node"] = "finalize_report"

    try:
        # ドラフトレポートを最終レポートとして保存
        state["final_report"] = state.get("draft_report", {})

        logger.info("Final report created", extra={"category": "RUN"})

    except Exception as e:
        logger.error(f"Report finalization failed: {e}", extra={"category": "RUN"})
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({"node": "finalize_report", "error": str(e)})
        raise

    return state
