from typing import Dict, List

import httpx
from sqlalchemy.engine.row import RowMapping

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.settings import settings
from content_discovery.web.api.feed.schema import FeedPack, Snap


def get_user_info(user_id: str) -> tuple[str, str, str]:
    """Returns username and fullname of user."""
    try:
        author = httpx.get(_url_get_user(user_id)).json()

        photo_url = author["profile_photo_id"]
        username = author["username"]
        first_name = author["first_name"]
        last_name = author["last_name"]

        fullname = f"{first_name} {last_name}"
        return (username, fullname, photo_url)
    except Exception:
        return ("Unknown", "Unknown", "Unknown")


def followed_users(user_id: str) -> List[Dict[str, str]]:
    """
    Returns a list of users that the user follows.

    Example:
    {
        "id": "greta",
        "first_name": null,
        "last_name": null,
        "username": "gretaa",
        "phone_number": null,
        "bio_msg": null,
        "profile_photo_id": null,
        "ubication": null,
        "is_followed": true
    }
    """
    return httpx.get(_url_get_following(user_id)).json() + [{"id": user_id}]


def followers(user_id: str) -> List[Dict[str, str]]:
    """Returns a list of users that follow the user."""
    return httpx.get(_url_get_followers(user_id)).json()


def _url_get_followers(user_id: str) -> str:
    return f"{settings.identity_socializer_url}/api/interactions/{user_id}/followers"


def _url_get_following(user_id: str) -> str:
    return f"{settings.identity_socializer_url}/api/interactions/{user_id}/following"


def _url_get_user(user_id: str) -> str:
    return f"{settings.identity_socializer_url}/api/auth/users/{user_id}"


async def complete_snaps(
    snaps: List[SnapsModel],
    user_id: str,
    snap_dao: SnapDAO,
) -> FeedPack:
    """Returns a list of snaps with additional information."""
    my_snaps = []

    for snap in snaps:
        completed_snap = await complete_snap(snap, user_id, snap_dao)
        my_snaps.append(completed_snap)

    return FeedPack(snaps=my_snaps)


async def complete_snaps_and_shares(
    snaps: List[RowMapping],
    user_id: str,
    snap_dao: SnapDAO,
) -> FeedPack:
    """Returns a list of snaps with additional information."""
    my_snaps = []

    for snap_data in snaps:
        completed_snap = await complete_snap_and_share(snap_data, user_id, snap_dao)
        my_snaps.append(completed_snap)

    return FeedPack(snaps=my_snaps)


async def complete_snap(
    snap: SnapsModel,
    user_id: str,
    snaps_dao: SnapDAO,
) -> Snap:
    """Returns a snap with additional information."""
    (username, fullname, url) = get_user_info(snap.user_id)

    has_shared = await snaps_dao.user_has_shared(user_id, snap.id)
    has_liked = await snaps_dao.user_has_liked(user_id, snap.id)
    num_replies = await snaps_dao.count_replies_by_snap(snap.id)

    return Snap(
        id=snap.id,
        author=snap.user_id,
        content=snap.content,
        likes=snap.likes,
        shares=snap.shares,
        favs=snap.favs,
        created_at=snap.created_at,
        username=username,
        fullname=fullname,
        parent_id=snap.parent_id,
        visibility=snap.visibility,
        privacy=snap.privacy,
        num_replies=num_replies,
        has_shared=has_shared,
        has_liked=has_liked,
        profile_photo_url=url,
    )


async def complete_snap_and_share(
    snap: RowMapping,
    user_id: str,
    snaps_dao: SnapDAO,
) -> Snap:
    """Returns a snap with additional information about sharing."""
    (username, fullname, url) = get_user_info(snap["SnapsModel"].user_id)

    has_shared = await snaps_dao.user_has_shared(user_id, snap["SnapsModel"].id)
    has_liked = await snaps_dao.user_has_liked(user_id, snap["SnapsModel"].id)
    num_replies = await snaps_dao.count_replies_by_snap(snap["SnapsModel"].id)

    if snap["ShareModel"]:
        (username, fullname, url) = get_user_info(snap["ShareModel"].user_id)
        was_shared_by = [username] if username else []
    else:
        was_shared_by = []

    snap = snap["SnapsModel"]
    return Snap(
        id=snap.id,
        author=snap.user_id,
        content=snap.content,
        likes=snap.likes,
        shares=snap.shares,
        favs=snap.favs,
        created_at=snap.created_at,
        username=username,
        fullname=fullname,
        parent_id=snap.parent_id,
        visibility=snap.visibility,
        privacy=snap.privacy,
        num_replies=num_replies,
        has_shared=has_shared,
        has_liked=has_liked,
        profile_photo_url=url,
        is_shared_by=was_shared_by,
    )


async def complete_snap_and_share(
    snap: RowMapping,
    user_id: str,
    snaps_dao: SnapDAO,
) -> Snap:
    """Returns a snap with additional information about sharing."""
    (username, fullname, url) = get_user_info(snap["SnapsModel"].user_id)

    has_shared = await snaps_dao.user_has_shared(user_id, snap["SnapsModel"].id)
    has_liked = await snaps_dao.user_has_liked(user_id, snap["SnapsModel"].id)
    num_replies = await snaps_dao.count_replies_by_snap(snap["SnapsModel"].id)

    if snap["ShareModel"]:
        (username, fullname, url) = get_user_info(snap["ShareModel"].user_id)
        was_shared_by = [username] if username else []
    else:
        was_shared_by = []

    snap = snap["SnapsModel"]
    return Snap(
        id=snap.id,
        author=snap.user_id,
        content=snap.content,
        likes=snap.likes,
        shares=snap.shares,
        favs=snap.favs,
        created_at=snap.created_at,
        username=username,
        fullname=fullname,
        parent_id=snap.parent_id,
        visibility=snap.visibility,
        num_replies=num_replies,
        has_shared=has_shared,
        has_liked=has_liked,
        profile_photo_url=url,
        is_shared_by=was_shared_by,
    )
