"""Workflow state for Hermes agents"""

from typing import TypedDict, List, Dict, Any, Optional


class WorkflowState(TypedDict, total=False):
    """LangGraphワークフロー状態"""

    # 入力
    original_prompt: str
    normalized_prompt: str
    config: Dict[str, Any]

    # クエリ生成
    queries: List[str]

    # 検索結果
    search_responses: List[Dict[str, Any]]
    scraped_contents: List[Dict[str, Any]]

    # 処理結果
    summarized_data: str

    # レポート
    draft_report: Dict[str, Any]
    final_report: Dict[str, Any]

    # 検証
    validation_loop: int
    validation_issues: List[str]
    additional_queries: List[str]

    # メタ情報
    start_time: str
    current_node: str
    errors: List[Dict[str, Any]]
