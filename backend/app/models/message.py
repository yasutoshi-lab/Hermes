"""Message model for chat log storage."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from backend.app.db.base import Base, utc_now


class MessageSender(str, Enum):
    """Message sender type enumeration."""
    USER = "user"
    SYSTEM = "system"


class Message(Base):
    """
    Message model for storing chat conversation logs.

    Attributes:
        id: Primary key
        task_id: Foreign key to tasks table (optional, for task-specific messages)
        sender: Message sender (user/system)
        content: Message content
        timestamp: Message timestamp (UTC)
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True)
    sender = Column(SQLEnum(MessageSender), nullable=False, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)

    # Relationships
    task = relationship("Task", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, sender='{self.sender}', task_id={self.task_id})>"
