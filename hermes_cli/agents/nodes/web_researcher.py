"""Web research node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState
from hermes_cli.tools.container_use_client import SearxNGClient


async def search_web(state: WorkflowState) -> WorkflowState:
    """Web検索実行"""
    logger.info("Searching web", extra={"category": "RUN"})

    state["current_node"] = "search_web"

    try:
        config = state["config"]
        search_config = config.get("search", {})

        client = SearxNGClient(
            searxng_url=search_config.get("searxng_base_url", "http://localhost:8080"),
            redis_url=search_config.get("redis_url", "redis://localhost:6379/0"),
            cache_ttl=search_config.get("cache_ttl", 3600),
        )

        # 追加クエリがあれば使用
        queries = state.get("additional_queries", []) or state["queries"]
        min_search = search_config.get("min_search", 3)
        max_search = search_config.get("max_search", 8)

        search_responses = []
        for query in queries:
            try:
                response = await client.search(query, num_results=max_search)
                search_responses.append(response.model_dump())
                logger.info(
                    f"Search completed for query: {query}",
                    extra={"category": "WEB", "results": len(response.results)},
                )
            except Exception as e:
                logger.warning(
                    f"Search failed for query '{query}': {e}",
                    extra={"category": "WEB"},
                )

        state["search_responses"] = search_responses

        # 追加クエリをクリア
        if "additional_queries" in state:
            state["additional_queries"] = []

        await client.close()

    except Exception as e:
        logger.error(f"Web search failed: {e}", extra={"category": "RUN"})
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({"node": "search_web", "error": str(e)})
        raise

    return state
