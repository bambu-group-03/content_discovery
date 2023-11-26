import datetime
import re
import uuid
from typing import List

from fastapi import Depends
from sqlalchemy import RowMapping, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.constants import Visibility
from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.hashtag_model import HashtagModel
from content_discovery.db.models.snaps_model import SnapsModel


class HashtagDAO:
    """Class for accessing hashtags table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_hashtag_model(
        self,
        snap_id: uuid.UUID,
        hashtag: str,
    ) -> None:
        """Add single hashtag to session."""
        try:
            ht = HashtagModel(snap_id=snap_id, name=hashtag)
            self.session.add(ht)

            return

        except Exception:
            return

    async def create_hashtags(
        self,
        snap_id: uuid.UUID,
        content: str,
    ) -> None:
        """Create hashtags from snap content."""
        if "#" in content:
            hashtags = re.findall(r"(?:^|\s)(#\w+)", content)

            for hashtag in hashtags:
                await self.create_hashtag_model(snap_id, hashtag)

    async def filter_hashtags(
        self,
        name: str,
    ) -> List[SnapsModel]:
        """Get list of filtered snaps by hashtag."""
        query = select(SnapsModel).distinct()
        query = query.where(SnapsModel.visibility == Visibility.PUBLIC.value)
        query = query.join(HashtagModel.snap)
        query = query.filter(HashtagModel.name.ilike(f"%{name}%"))

        rows = await self.session.execute(query)

        return list(rows.scalars().fetchall())

    async def get_top_hashtags(
        self,
        cutoff_date: datetime.datetime,
        minimum_hashtag_count: int,
    ) -> List[RowMapping]:
        """Get counts of the most common hashtags within a timeframe"""
        query = select(HashtagModel.name, func.count(HashtagModel.name).label("count"))
        query = query.where(HashtagModel.created_at > cutoff_date)
        query = query.group_by(HashtagModel.name)
        query = query.having(
            func.count(HashtagModel.name) >= minimum_hashtag_count,
        )
        rows = await self.session.execute(query)
        return list(rows.mappings().fetchall())
