import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String, Uuid

from content_discovery.db.base import Base


class TrendingTopicModel(Base):
    """Model for trending topic."""

    __tablename__ = "topics"

    length = 100

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        default=uuid.uuid4,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(length))


class TrendingModel(Base):
    """Model for topic-snap relationship."""

    __tablename__ = "relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        default=uuid.uuid4,
        primary_key=True,
    )
    snap_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("snaps.id"),
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("topics.id"),
    )

    snap = relationship("SnapsModel", foreign_keys=[snap_id])
    topic = relationship("TrendingTopicModel", foreign_keys=[topic_id])
