"""Task result model for storing analysis and summary outputs."""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base, utc_now


class TaskResult(Base):
    """
    Task result model for storing summarization and analysis outputs.

    Attributes:
        id: Primary key
        task_id: Foreign key to tasks table
        summary_text: Generated summary of the document
        analysis_text: Detailed analysis including novelty, strengths, issues
        created_at: Result creation timestamp (UTC)
    """

    __tablename__ = "task_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    summary_text = Column(Text, nullable=True)
    analysis_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    task = relationship("Task", back_populates="result", foreign_keys=[task_id])

    def __repr__(self) -> str:
        return f"<TaskResult(id={self.id}, task_id={self.task_id})>"
