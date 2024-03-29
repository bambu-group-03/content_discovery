import datetime
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime, String, Uuid

from content_discovery.db.base import Base


class LikeModel(Base):
    """Model for like model."""

    __tablename__ = "likes"

    length = 200

    user_id: Mapped[str] = mapped_column(String(length), primary_key=True)
    snap_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("snaps.id"),
        primary_key=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
    )

    snap = relationship("SnapsModel", foreign_keys=[snap_id])
