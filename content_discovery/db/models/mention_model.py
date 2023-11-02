import datetime
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime, String, Uuid

from content_discovery.db.base import Base


class MentionModel(Base):
    """Model for mention model."""

    __tablename__ = "mentions"

    length = 200

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        default=uuid.uuid4,
        primary_key=True,
    )
    mentioned_id: Mapped[str] = mapped_column(String(length))
    mentioned_username: Mapped[str] = mapped_column(String(length))
    snap_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("snaps.id"),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
    )

    snap = relationship("SnapsModel", foreign_keys=[snap_id])
