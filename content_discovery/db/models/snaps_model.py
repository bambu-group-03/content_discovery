import datetime
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String, Uuid

from content_discovery.db.base import Base

TWEET_LEN = 280


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
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow(),
    )
