import datetime
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime, String, Uuid

from content_discovery.db.base import Base


class FavModel(Base):
    """Model for fav model."""

    __tablename__ = "favs"

    length = 200

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        default=uuid.uuid4,
        primary_key=True,
    )
    user_id: Mapped[str] = mapped_column(String(length))
    snap_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("snaps.id"))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow(),
    )

    snap = relationship("SnapsModel", foreign_keys=[snap_id])

