from typing import Any

from fastapi import APIRouter, Depends

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO

router = APIRouter()


@router.get("/get_all", response_model=None)
async def get_all(
    topic_dao: TrendingTopicDAO = Depends(),
    hashtag_dao: HashtagDAO = Depends(),
) -> Any:
    """Returns all topics."""
    tts = []

    topics = await topic_dao.get_all_topics()
    for tt in topics:
        topic = {
            "id": tt.id,
            "name": tt.name,
            "created_at": tt.created_at,
            "times_used": await hashtag_dao.get_times_used_by_hashtag(tt.name),
        }
        tts.append(topic)

    return tts
