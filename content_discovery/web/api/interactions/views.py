import datetime
from typing import Any, List

import httpx
from fastapi import APIRouter
from fastapi.param_functions import Depends

from content_discovery.db.dao.fav_dao import FavDAO
from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.like_dao import LikeDAO
from content_discovery.db.dao.mention_dao import MentionDAO
from content_discovery.db.dao.share_dao import ShareDAO
from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.notifications import Notifications
from content_discovery.web.api.feed.schema import FeedPack
from content_discovery.web.api.utils import complete_snaps

router = APIRouter()


@router.post("/{user_id}/like/{snap_id}")
async def like_snap(
    user_id: str,
    snap_id: str,
    like_dao: LikeDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> Any:
    """User likes a snap."""
    # Create like in db
    like = await like_dao.create_like_model(user_id=user_id, snap_id=snap_id)

    if not like:
        return None

    # Increase likes from snap
    await snap_dao.increase_likes(snap_id)

    snap = await snap_dao.get_snap_from_id(snap_id)

    if not snap:
        return httpx.Response(status_code=404)

    # send new like notification
    await Notifications().send_like_notification(
        from_id=user_id,
        to_id=snap.user_id,
        snap_id=snap_id,
        snap_dao=snap_dao,
    )


@router.delete("/{user_id}/unlike/{snap_id}")
async def unlike_snap(
    user_id: str,
    snap_id: str,
    like_dao: LikeDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> None:
    """User unlikes a snap."""
    # Check if like exists
    like = await like_dao.get_like_model(user_id, snap_id)

    if not like:
        return

    # Delete like from db
    await like_dao.delete_like_model(user_id, snap_id)

    # Decrease likes from snap
    await snap_dao.decrease_likes(snap_id)


@router.post("/{user_id}/share/{snap_id}")
async def share_snap(
    user_id: str,
    snap_id: str,
    share_dao: ShareDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> None:
    """User shares a snap."""
    # Create share in db
    share = await share_dao.create_share_model(user_id, snap_id)

    if not share:
        return

    # Increase shares from snap
    await snap_dao.increase_shares(snap_id)


@router.delete("/{user_id}/unshare/{snap_id}")
async def unshare_snap(
    user_id: str,
    snap_id: str,
    share_dao: ShareDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> None:
    """User unshare a snap."""
    # Check if share exists
    share = await share_dao.get_share_model(user_id, snap_id)

    if not share:
        return

    # Delete share from db // TODO fix this
    await share_dao.delete_share_model(user_id, snap_id)

    # Decrease shares from snap
    await snap_dao.decrease_shares(snap_id)


@router.post("/{user_id}/fav/{snap_id}")
async def fav_snap(
    user_id: str,
    snap_id: str,
    fav_dao: FavDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> None:
    """User favs a snap."""
    # Create fav in db
    fav = await fav_dao.create_fav_model(user_id, snap_id)

    if not fav:
        return

    # Increase favs from snap
    await snap_dao.increase_favs(snap_id)


@router.delete("/{user_id}/unfav/{snap_id}")
async def unfav_snap(
    user_id: str,
    snap_id: str,
    fav_dao: FavDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> None:
    """User unfav a snap."""
    # Check if fav exists
    fav = await fav_dao.get_fav_model(user_id, snap_id)

    if not fav:
        return

    # Delete fav from db
    await fav_dao.delete_fav_model(user_id, snap_id)

    # Decrease favs from snap
    await snap_dao.decrease_favs(snap_id)


@router.get("/{user_id}/favs")
async def get_favs(
    user_id: str,
    fav_dao: FavDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snaps that the user has fav'd."""
    snaps = await fav_dao.get_favs_by_user(user_id)
    return await complete_snaps(snaps, user_id, snap_dao)


@router.post("/{user_id}/set_public/{snap_id}")
async def make_snap_public(
    user_id: str,
    snap_id: str,
    snap_dao: SnapDAO = Depends(),
) -> None:
    """User makes a snap public."""
    await snap_dao.make_public(snap_id)


@router.post("/{user_id}/set_private/{snap_id}")
async def make_snap_private(
    user_id: str,
    snap_id: str,
    snap_dao: SnapDAO = Depends(),
) -> None:
    """User makes a snap private."""
    await snap_dao.make_private(snap_id)


@router.get("/mentions/{user_id}")
async def get_mentioned_snap_by_id(
    user_id: str,
    mention_dao: MentionDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snaps where the user is mentioned."""
    snaps = await mention_dao.get_mentions(user_id)
    return await complete_snaps(snaps, user_id, snap_dao)


# test
@router.get("/hashtags/top")
async def get_top_hashtags(hashtag_dao: HashtagDAO = Depends()) -> List[Any]:
    """Get hashtags with more than 4 appearances in the hashtag table."""
    list_of_rows = await hashtag_dao.get_top_hashtags(
        datetime.datetime(2000, 1, 1, 1, 1, 1),
        4,
    )
    return [str(elem) for elem in list_of_rows]
