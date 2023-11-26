import datetime
import re
import uuid
from typing import List

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.constants import Visibility
from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.hashtag_model import HashtagModel
from content_discovery.db.models.snaps_model import SnapsModel


class HashtagDAO:
    """Class for accessing hashtags table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_hashtag_model(self, snap_id: uuid.UUID, hashtag: str) -> None:
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

    async def get_top_hashtags(self, period: datetime.timedelta, max: int):
        cutoff_date = datetime.datetime(year=2022, month=1, day=1)
        minimum_hashtag_count_to_be_a_trend = 4
        query = select(HashtagModel.name, func.count(HashtagModel.name).label("count")) \
            .where(HashtagModel.created_at > cutoff_date) \
            .group_by(HashtagModel.name) \
            .having(func.count(HashtagModel.name) >= minimum_hashtag_count_to_be_a_trend)
        rows = await self.session.execute(query)
        return list(rows.mappings().fetchall())
