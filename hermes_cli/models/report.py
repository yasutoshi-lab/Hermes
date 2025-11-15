"""Report models for Hermes"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Citation(BaseModel):
    """引用情報"""

    index: int
    url: str
    title: str
    accessed_at: datetime


class ReportSection(BaseModel):
    """レポートセクション"""

    title: str
    content: str
    citations: List[int] = Field(default_factory=list)


class Report(BaseModel):
    """レポート"""

    title: str
    sections: List[ReportSection]
    citations: List[Citation]

    def to_markdown(self) -> str:
        """Markdown形式で出力"""
        md = f"# {self.title}\n\n"

        for section in self.sections:
            md += f"## {section.title}\n\n"
            md += f"{section.content}\n\n"

        if self.citations:
            md += "## 参考文献\n\n"
            for cite in self.citations:
                md += f"[{cite.index}] {cite.title}  \n{cite.url}\n\n"

        return md


class ReportMetadata(BaseModel):
    """レポートメタデータ"""

    task_id: str
    status: Literal["success", "failed"]
    start_at: datetime
    finish_at: datetime
    duration: float  # 秒
    model: str
    loops: int  # 実行した検証ループ数
    sources: int  # 収集ソース数
    error: Optional[str] = None

    def to_yaml(self) -> str:
        """YAML形式で出力"""
        import yaml

        return yaml.dump(self.model_dump(mode="json"), allow_unicode=True, default_flow_style=False)
