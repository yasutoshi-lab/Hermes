"""Search result models for Hermes"""

from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class SearchResult(BaseModel):
    """単一検索結果"""

    title: str
    url: str
    snippet: str
    engine: Optional[str] = None
    score: Optional[float] = None


class SearchResponse(BaseModel):
    """検索レスポンス"""

    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class ScrapedContent(BaseModel):
    """スクレイプコンテンツ"""

    url: str
    title: str
    content: str
    extracted_at: datetime = Field(default_factory=datetime.now)
    word_count: int = 0

    @field_validator("word_count", mode="before")
    @classmethod
    def set_word_count(cls, v, info) -> int:
        if v == 0 and "content" in info.data:
            return len(info.data["content"].split())
        return v
