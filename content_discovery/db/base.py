from sqlalchemy.orm import DeclarativeBase

from content_discovery.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
