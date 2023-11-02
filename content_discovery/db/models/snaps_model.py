import datetime
import uuid
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime, Integer, String, Uuid

from content_discovery.db.base import Base


class Visibility(Enum):
    """Enum for the visibility of a snap"""

    PUBLIC = 1
    PRIVATE = 2


class SnapsModel(Base):
    """Model for demo purpose."""

    __tablename__ = "snaps"

    length = 280

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        default=uuid.uuid4,
        primary_key=True,
    )
    user_id: Mapped[str] = mapped_column(String(length))
    parent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("snaps.id"),
        nullable=True,
    )
    content: Mapped[str] = mapped_column(String(length))
    likes: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    favs: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
    )

    visibility: Mapped[int] = mapped_column(Integer, default=Visibility.PUBLIC)

    snap = relationship("SnapsModel", foreign_keys=[parent_id])
