"""Base class for SQLAlchemy models."""
from sqlalchemy.orm import DeclarativeBase, declared_attr
from datetime import datetime, timezone


class Base(DeclarativeBase):
    """Base class for all database models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name."""
        return cls.__name__.lower() + 's'

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


def utc_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)
