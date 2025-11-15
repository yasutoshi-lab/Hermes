"""Draft report creation node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState
from datetime import datetime


def create_draft(state: WorkflowState) -> WorkflowState:
    """ドラフトレポート作成"""
    logger.info("Creating draft report", extra={"category": "RUN"})

    state["current_node"] = "create_draft"

    try:
        # 簡易レポート作成
        citations = []
        citation_index = 1

        for response in state["search_responses"]:
            for result in response.get("results", []):
                citations.append(
                    {
                        "index": citation_index,
                        "url": result["url"],
                        "title": result["title"],
                        "accessed_at": datetime.now().isoformat(),
                    }
                )
                citation_index += 1

        draft_report = {
            "title": f"調査レポート: {state['normalized_prompt'][:50]}",
            "sections": [
                {
                    "title": "調査結果",
                    "content": state.get("summarized_data", ""),
                    "citations": list(range(1, len(citations) + 1)),
                }
            ],
            "citations": citations,
        }

        state["draft_report"] = draft_report

        logger.info("Draft report created", extra={"category": "RUN"})

    except Exception as e:
        logger.error(f"Draft creation failed: {e}", extra={"category": "RUN"})
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({"node": "create_draft", "error": str(e)})
        raise

    return state
