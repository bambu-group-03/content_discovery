from fastapi import APIRouter
from fastapi.param_functions import Depends

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.web.api.feed.schema import FeedPack, Snap
from content_discovery.web.api.feed.views import get_user_info

router = APIRouter()


@router.get("/hashtag", response_model=None)
async def filter_hashtags(
    user_id: str,
    hashtag: str,
    hashtag_dao: HashtagDAO = Depends(),
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Retrieve a list of filtered snaps by hashtags."""
    my_snaps = []

    snaps = await hashtag_dao.filter_hashtags(hashtag)

    for snap in snaps:
        has_shared = await snaps_dao.user_has_shared(user_id, snap.id)
        has_liked = await snaps_dao.user_has_liked(user_id, snap.id)

        (username, fullname) = get_user_info(snap.user_id)

        my_snaps.append(
            Snap(
                id=snap.id,
                author=str(snap.user_id),
                content=snap.content,
                likes=snap.likes,
                shares=snap.shares,
                favs=snap.favs,
                created_at=snap.created_at,
                parent_id=snap.parent_id,
                username=username,
                fullname=fullname,
                visibility=snap.visibility,
                has_shared=has_shared,
                has_liked=has_liked,
            ),
        )

    return FeedPack(snaps=my_snaps)


@router.get("/content", response_model=None)
async def filter_snaps(
    user_id: str,
    content: str,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Retrieve a list of filtered snaps by content."""
    my_snaps = []

    snaps = await snaps_dao.filter_snaps(content)

    for snap in snaps:

        has_shared = await snaps_dao.user_has_shared(user_id, snap.id)
        has_liked = await snaps_dao.user_has_liked(user_id, snap.id)

        (username, fullname) = get_user_info(snap.user_id)

        my_snaps.append(
            Snap(
                id=snap.id,
                author=str(snap.user_id),
                content=snap.content,
                likes=snap.likes,
                shares=snap.shares,
                favs=snap.favs,
                created_at=snap.created_at,
                parent_id=snap.parent_id,
                username=username,
                fullname=fullname,
                visibility=snap.visibility,
                has_shared=has_shared,
                has_liked=has_liked,
            ),
        )

    return FeedPack(snaps=my_snaps)
