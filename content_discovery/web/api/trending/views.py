from fastapi import APIRouter, Depends

from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO

router = APIRouter()


@router.get("/trending")
async def get_trending(
    topic_dao: TrendingTopicDAO = Depends(),
) -> None:
    """Updates a snap."""
