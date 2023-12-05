from typing import List

from fastapi import APIRouter, Depends

from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO
from content_discovery.db.models.trending_model import TrendingTopicModel

router = APIRouter()


@router.get("/trending")
async def get_trending(
    topic_dao: TrendingTopicDAO = Depends(),
) -> None:
    """Updates a snap."""


@router.get("/get_all", response_model=None)
async def get_all(
    topic_dao: TrendingTopicDAO = Depends(),
) -> List[TrendingTopicModel]:
    """Returns all topics."""
    return await topic_dao.get_all_topics()
