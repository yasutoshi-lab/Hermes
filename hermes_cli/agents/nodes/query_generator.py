"""Query generation node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState
from hermes_cli.tools.ollama_client import OllamaClient


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
        queries = await client.generate_queries(state["normalized_prompt"], num_queries)

        state["queries"] = queries

        logger.info(
            f"Generated {len(queries)} queries",
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
