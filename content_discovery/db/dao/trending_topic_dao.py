import datetime
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.trending_model import TrendingTopicModel


class TrendingTopicDAO:
    """Class for accessing snap table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_topic_model(
        self,
        name: str,
    ) -> Optional[TrendingTopicModel]:
        """
        Add single snap to session.

        :param user_id
        :param content
        :param privacy
        """
        exists = await self.get_topic_from_name(name)
        if exists:
            return None
        topic = TrendingTopicModel(name=name)
        self.session.add(topic)
        await self.session.flush()
        await self.session.commit()
        return topic

    async def get_topic_from_name(
        self,
        name: str,
    ) -> Optional[TrendingTopicModel]:
        """Get specific topic model."""
        query = select(TrendingTopicModel).where(TrendingTopicModel.name == name)
        rows = await self.session.execute(query)
        return rows.scalars().first()

    async def get_all_topics(
        self,
    ) -> List[TrendingTopicModel]:
        """Get all trending topic models."""
        query = select(TrendingTopicModel)
        rows = await self.session.execute(query)
        return list(rows.scalars().all())

    async def delete_old_trending_topics(self, cutoff: datetime.timedelta) -> None:
        """Delete old trending topics."""
        query = delete(TrendingTopicModel)
        query = query.where(
            TrendingTopicModel.created_at < datetime.datetime.now() - cutoff,
        )

        await self.session.execute(query)
        await self.session.commit()
