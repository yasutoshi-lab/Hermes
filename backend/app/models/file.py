"""File model for uploaded file metadata."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base, utc_now


class File(Base):
    """
    File model for storing uploaded file metadata.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        file_name: Original filename
        storage_path: Path where file is stored on disk
        uploaded_at: Upload timestamp (UTC)
    """

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="files")

    def __repr__(self) -> str:
        return f"<File(id={self.id}, file_name='{self.file_name}', user_id={self.user_id})>"
