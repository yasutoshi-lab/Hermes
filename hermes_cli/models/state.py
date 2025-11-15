"""Workflow state model for Hermes"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from hermes_cli.models.search import SearchResponse, ScrapedContent
    from hermes_cli.models.report import Report


class WorkflowState(BaseModel):
    """LangGraphワークフロー状態"""

    # 入力
    original_prompt: str
    normalized_prompt: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)

    # クエリ生成
    queries: List[str] = Field(default_factory=list)

    # 検索結果
    search_responses: List[Dict[str, Any]] = Field(default_factory=list)
    scraped_contents: List[Dict[str, Any]] = Field(default_factory=list)

    # 処理結果
    summarized_data: Optional[str] = None

    # レポート
    draft_report: Optional[Dict[str, Any]] = None
    final_report: Optional[Dict[str, Any]] = None

    # 検証
    validation_loop: int = 0
    validation_issues: List[str] = Field(default_factory=list)

    # メタ情報
    start_time: datetime = Field(default_factory=datetime.now)
    current_node: Optional[str] = None
    errors: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
