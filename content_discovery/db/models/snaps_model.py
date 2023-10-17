from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from content_discovery.db.base import Base

TWEET_LEN = 280


class SnapsModel(Base):
    """Model for demo purpose."""

    __tablename__ = "snaps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    content: Mapped[str] = mapped_column(String(length=TWEET_LEN))
