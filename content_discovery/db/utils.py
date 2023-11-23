import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from content_discovery.constants import Visibility
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.settings import settings


async def create_database() -> None:
    """Create a database."""
    db_url = make_url(str(settings.db_url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{settings.db_base}'",  # noqa: E501, S608
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_database()

    async with engine.connect() as conn:  # noqa: WPS440
        await conn.execute(
            text(
                f'CREATE DATABASE "{settings.db_base}" ENCODING "utf8" TEMPLATE template1',  # noqa: E501
            ),
        )


async def drop_database() -> None:
    """Drop current database."""
    db_url = make_url(str(settings.db_url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{settings.db_base}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE "{settings.db_base}"'))


def is_valid_uuid(value: Any) -> bool:
    """Check if value is a valid uuid."""
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False


from sqlalchemy import or_


def query_visibility_filter() -> Any:
    "Snap visibility is public"
    return SnapsModel.visibility == Visibility.PUBLIC.value


def default_visibility() -> int:
    return Visibility.PUBLIC.value


def private_visibility() -> int:
    return Visibility.PRIVATE.value


def query_privacy_filter_to_only_followers(followed_by_user) -> Any:
    """
    Get query expression for: snap.privacy = 1 OR snap.user_id IN [followed1, followed2]
    this function pings identity socializer to resolve followed users
    """
    followed_by_user_list = list(map(lambda dict: dict["id"], followed_by_user))
    return or_(
        SnapsModel.privacy == 1,
        SnapsModel.user_id.in_(followed_by_user_list),
    )


"""
def _filter_privacy_to_only_mutuals_of_author(user_id):
    _mutuals = mutuals(user_id)
    return or_(SnapsModel.privacy == 1,
               SnapsModel.user_id.in_(mutuals))
"""
