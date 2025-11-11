"""Task model for managing summarization and analysis tasks."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from enum import Enum
from backend.app.db.base import Base, utc_now


class TaskType(str, Enum):
    """Task type enumeration."""
    SUMMARY = "summary"
    SEARCH = "search"
    ANALYSIS = "analysis"


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAIL = "fail"


class Task(Base):
    """
    Task model for managing document summarization and analysis tasks.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        task_type: Type of task (summary/search/analysis)
        file_path: Path to the file to process (optional)
        model_name: Name of the LLM model to use
        schedule_time: Scheduled execution time (optional)
        status: Current task status
        result_id: Foreign key to task_results (optional)
        error_msg: Error message if task failed
        created_at: Task creation timestamp (UTC)
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(SQLEnum(TaskType), nullable=False, index=True)
    file_path = Column(String(500), nullable=True)
    model_name = Column(String(100), nullable=False, default="gpt-oss:20b")
    schedule_time = Column(DateTime(timezone=True), nullable=True, index=True)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    result_id = Column(Integer, ForeignKey("task_results.id", ondelete="SET NULL"), nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="tasks")
    result = relationship("TaskResult", back_populates="task", foreign_keys=[result_id])
    messages = relationship("Message", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, type='{self.task_type}', status='{self.status}', user_id={self.user_id})>"
