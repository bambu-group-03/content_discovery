from typing import Any

from fastapi import APIRouter
from fastapi.param_functions import Depends

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.web.api.feed.schema import FeedPack
from content_discovery.web.api.utils import (
    complete_snaps,
    followed_users,
    get_user_info,
)

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
    users = followed_users(user_id)
    snaps = await snaps_dao.filter_snaps(content, users)
    return await complete_snaps(snaps, user_id, snaps_dao)


@router.get("/admin/content", response_model=None)
async def admin_filter_snaps(
    content: str,
    snaps_dao: SnapDAO = Depends(),
) -> Any:
    """Retrieve a list of filtered snaps by content."""
    completed_snaps = []

    snaps = await snaps_dao.admin_filter_snaps(content)

    for snap in snaps:
        (username, fullname, _url) = get_user_info(snap.user_id)

        completed_snaps.append(
            {
                "id": snap.id,
                "user_id": snap.user_id,
                "content": snap.content,
                "likes": snap.likes,
                "shares": snap.shares,
                "favs": snap.favs,
                "created_at": snap.created_at,
                "username": username,
                "fullname": fullname,
                "parent_id": snap.parent_id,
                "visibility": snap.visibility,
                "privacy": snap.privacy,
            },
        )

    return completed_snaps
