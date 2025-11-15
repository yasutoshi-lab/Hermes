"""Task models for Hermes"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from pathlib import Path


class TaskOptions(BaseModel):
    """タスク固有オプション"""

    language: Optional[str] = None
    query_count: Optional[int] = None
    min_validation: Optional[int] = None
    max_validation: Optional[int] = None


class Task(BaseModel):
    """タスク定義"""

    id: str = Field(..., pattern=r"^\d{4}-\d{4}$", description="タスクID (YYYY-NNNN)")
    prompt: str = Field(..., min_length=1, description="調査プロンプト")
    status: Literal["scheduled", "running", "completed", "failed"] = "scheduled"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    options: Optional[TaskOptions] = None

    def to_yaml(self) -> str:
        """YAML形式で出力"""
        import yaml

        return yaml.dump(self.model_dump(mode="json"), allow_unicode=True, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "Task":
        """YAML形式から読み込み"""
        import yaml

        data = yaml.safe_load(yaml_str)
        return cls(**data)

    def save(self, task_dir: Path) -> None:
        """ファイルに保存"""
        file_path = task_dir / f"{self.id}.yaml"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())
