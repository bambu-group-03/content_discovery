import datetime
import uuid
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime, Integer, String, Uuid

from content_discovery.db.base import Base
from content_discovery.db.models.fav_model import FavModel


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
    content: Mapped[str] = mapped_column(String(length))
    likes: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    favs: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
    )

    list_favs: Mapped[List["FavModel"]] = relationship(
        back_populates="snap",
        cascade="all, delete",
    )
