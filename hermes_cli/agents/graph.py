"""Workflow graph definition for Hermes"""

from langgraph.graph import StateGraph, END
from hermes_cli.agents.state import WorkflowState
from hermes_cli.agents.nodes import (
    normalize_prompt,
    generate_queries,
    search_web,
    process_contents,
    create_draft,
    validate_report,
    should_continue_validation,
    finalize_report,
)


def create_workflow() -> StateGraph:
    """Hermesワークフロー作成"""

    workflow = StateGraph(WorkflowState)

    # ノード追加
    workflow.add_node("normalize", normalize_prompt)
    workflow.add_node("generate_queries", generate_queries)
    workflow.add_node("search", search_web)
    workflow.add_node("process", process_contents)
    workflow.add_node("draft", create_draft)
    workflow.add_node("validate", validate_report)
    workflow.add_node("finalize", finalize_report)

    # エッジ定義
    workflow.set_entry_point("normalize")
    workflow.add_edge("normalize", "generate_queries")
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "process")
    workflow.add_edge("process", "draft")
    workflow.add_edge("draft", "validate")

    # 条件分岐
    workflow.add_conditional_edges(
        "validate",
        should_continue_validation,
        {
            "search": "search",  # 追加検索
            "finalize": "finalize",  # 終了
        },
    )

    workflow.add_edge("finalize", END)

    # 検証ループ対応のため再帰制限を増やす
    return workflow.compile({"recursion_limit": 50})
