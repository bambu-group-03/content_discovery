from fastapi import APIRouter
from fastapi.param_functions import Depends

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.web.api.feed.schema import FeedPack
from content_discovery.web.api.utils import complete_snaps, followed_users_ids

router = APIRouter()


@router.get("/hashtag", response_model=None)
async def filter_hashtags(
    user_id: str,
    hashtag: str,
    hashtag_dao: HashtagDAO = Depends(),
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Retrieve a list of filtered snaps by hashtags."""
    snaps = await hashtag_dao.filter_hashtags(hashtag)

    return await complete_snaps(snaps, user_id, snaps_dao)


@router.get("/content", response_model=None)
async def filter_snaps(
    user_id: str,
    content: str,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Retrieve a list of filtered snaps by content."""
    users = followed_users_ids(user_id)
    snaps = await snaps_dao.filter_snaps(content, users)
    return await complete_snaps(snaps, user_id, snaps_dao)
