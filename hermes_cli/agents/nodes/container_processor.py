"""Content processing node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState
from hermes_cli.tools.ollama_client import OllamaClient


async def process_contents(state: WorkflowState) -> WorkflowState:
    """コンテンツ処理・要約"""
    logger.info("Processing contents", extra={"category": "RUN"})

    state["current_node"] = "process_contents"

    try:
        config = state["config"]
        ollama_config = config.get("ollama", {})

        client = OllamaClient(
            api_url=ollama_config.get("api_url", "http://localhost:11434/api/chat"),
            model=ollama_config.get("model", "gpt-oss:20b"),
            timeout=ollama_config.get("timeout", 120),
            retry=ollama_config.get("retry", 3),
        )

        # 検索結果からコンテンツ抽出
        contents = []
        for response in state["search_responses"]:
            for result in response.get("results", []):
                content = f"タイトル: {result['title']}\nURL: {result['url']}\n内容: {result['snippet']}"
                contents.append(content)

        if contents:
            # 要約実行
            summarized = await client.summarize(contents, state["normalized_prompt"])
            state["summarized_data"] = summarized

            logger.info(
                f"Contents summarized: {len(contents)} sources",
                extra={"category": "RUN"},
            )
        else:
            state["summarized_data"] = "検索結果が見つかりませんでした。"
            logger.warning("No search results to process", extra={"category": "RUN"})

        await client.close()

    except Exception as e:
        logger.error(f"Content processing failed: {e}", extra={"category": "RUN"})
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append({"node": "process_contents", "error": str(e)})
        raise

    return state
