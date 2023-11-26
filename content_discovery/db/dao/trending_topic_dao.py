from fastapi import Depends
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
    ) -> TrendingTopicModel:
        """
        Add single snap to session.

        :param user_id
        :param content
        :param privacy
        """
        print("add_topic")
        topic = TrendingTopicModel(name=name)
        self.session.add(topic)
        await self.session.flush()
        await self.session.commit()
        return topic
