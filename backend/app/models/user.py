"""User model for authentication and user management."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.db.base import Base, utc_now


class User(Base):
    """
    User model for storing authentication information.

    Attributes:
        id: Primary key
        email: User's email address (unique)
        username: Display name for the user
        password_hash: Hashed password (using Argon2)
        created_at: Account creation timestamp (UTC)
        last_login: Last login timestamp (UTC)
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
