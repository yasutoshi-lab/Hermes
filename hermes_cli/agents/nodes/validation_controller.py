"""Validation loop controller"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState


def should_continue_validation(state: WorkflowState) -> str:
    """検証ループ継続判定"""
    # ループカウンタは validate_report ノード内で更新される
    loop_count = state.get("validation_loop", 0)

    config = state["config"]
    validation_config = config.get("validation", {})
    min_val = validation_config.get("min_validation", 1)
    max_val = validation_config.get("max_validation", 3)

    logger.info(
        f"Validation loop: {loop_count}/{max_val}",
        extra={"category": "RUN"},
    )

    # 最大回数到達
    if loop_count >= max_val:
        logger.info("Max validation reached, finalizing", extra={"category": "RUN"})
        return "finalize"

    # 連続して0件検索が発生している場合は検証を中止
    recent_searches = state.get("search_responses", [])[-3:]  # 直近3回の検索
    empty_search_count = sum(1 for r in recent_searches if len(r.get("results", [])) == 0)

    if empty_search_count >= 2:
        logger.warning(
            f"Multiple empty searches detected ({empty_search_count}/3), finalizing early",
            extra={"category": "RUN"},
        )
        return "finalize"

    # 検索が連続で失敗している場合は最小回数到達で終了
    search_responses = state.get("search_responses", [])
    has_results = any(len(r.get("results", [])) > 0 for r in search_responses)

    if not has_results and loop_count >= min_val:
        logger.info(
            "Search unavailable and min validation reached, finalizing",
            extra={"category": "RUN"},
        )
        return "finalize"

    # 最小回数未満は継続
    if loop_count < min_val:
        if state.get("additional_queries"):
            logger.info(
                "Min validation not reached, continuing",
                extra={"category": "RUN"},
            )
            return "search"
        else:
            # 追加クエリがない場合は終了
            logger.info("No additional queries, finalizing", extra={"category": "RUN"})
            return "finalize"

    # 問題がなければ終了
    if not state.get("validation_issues") and not state.get("additional_queries"):
        logger.info("No issues found, finalizing", extra={"category": "RUN"})
        return "finalize"

    # 追加クエリがあれば継続
    if state.get("additional_queries"):
        logger.info(
            f"Issues found: {len(state.get('validation_issues', []))}, continuing",
            extra={"category": "RUN"},
        )
        return "search"

    # それ以外は終了
    return "finalize"
