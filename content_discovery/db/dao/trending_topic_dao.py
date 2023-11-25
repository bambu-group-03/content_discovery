import uuid
from typing import Any, Dict, List, Optional, Union

from fastapi import Depends
from sqlalchemy import Select, delete, or_, outerjoin, select, update
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from content_discovery.constants import Visibility
from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.fav_model import FavModel
from content_discovery.db.models.hashtag_model import HashtagModel
from content_discovery.db.models.like_model import LikeModel
from content_discovery.db.models.mention_model import MentionModel
from content_discovery.db.models.share_model import ShareModel
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.db.models.trending_model import TrendingTopicModel
from content_discovery.db.utils import is_valid_uuid


class TrendingTopicDAO:
    """Class for accessing snap table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_topic_model(
        self,
        user_id: str,
        content: str,
        privacy: int,
    ) -> SnapsModel:
        """
        Add single snap to session.

        :param user_id
        :param content
        :param privacy
        """
        topic = TrendingTopicModel(name="Football" + str(self.VAR))
        self.session.add(topic)
        await self.session.flush()
