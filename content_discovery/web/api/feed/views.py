from typing import Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from sqlalchemy import inspect

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.mention_dao import MentionDAO
from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.settings import settings
from content_discovery.web.api.feed.schema import (
    FeedPack,
    PostSnap,
    ReplySnap,
    Snap,
    UpdateSnap,
)

router = APIRouter()

NON_EXISTENT = 405
OK = 200


@router.post("/post")
async def post_snap(
    incoming_message: PostSnap,
    snaps_dao: SnapDAO = Depends(),
    hashtag_dao: HashtagDAO = Depends(),
    mention_dao: MentionDAO = Depends(),
) -> Snap:
    """Uploads a snap with the received content."""
    snap = await snaps_dao.create_snaps_model(
        user_id=incoming_message.user_id,
        content=incoming_message.content,
    )

    await hashtag_dao.create_hashtags(snap.id, snap.content)
    await mention_dao.create_mentions(snap.id, snap.content)

    insp = inspect(snap)
    i_d = insp.attrs.id.value
    return Snap(
        id=i_d,
        author=str(insp.attrs.user_id.value),
        content=insp.attrs.content.value,
        likes=insp.attrs.likes.value,
        shares=insp.attrs.shares.value,
        favs=insp.attrs.favs.value,
        created_at=insp.attrs.created_at.value,
        username=None,
        fullname=None,
        parent_id=insp.attrs.parent_id.value,
        visibility=insp.attrs.visibility.value,
    )


@router.post("/reply", response_model=None)
async def reply_snap(
    incoming_message: ReplySnap,
    snaps_dao: SnapDAO = Depends(),
    hashtag_dao: HashtagDAO = Depends(),
    mention_dao: MentionDAO = Depends(),
) -> Optional[SnapsModel]:
    """Create a reply snap with the received content."""
    if not incoming_message.parent_id:
        return None

    reply = await snaps_dao.create_reply_snap(
        user_id=incoming_message.user_id,
        content=incoming_message.content,
        parent_id=incoming_message.parent_id,
    )

    if not reply:
        return None

    # Create hashtags and mentions
    await hashtag_dao.create_hashtags(reply.id, reply.content)
    await mention_dao.create_mentions(reply.id, reply.content)

    return reply


@router.put("/update_snap")
async def update_snap(
    body: UpdateSnap,
    snaps_dao: SnapDAO = Depends(),
) -> None:
    """Updates a snap."""
    await snaps_dao.update_snap(body.user_id, body.snap_id, body.content)


@router.delete("/snap/{snap_id}")
async def delete_snap(
    snap_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> None:
    """Deletes a snap."""
    await snaps_dao.delete_snap(snap_id)


@router.get("/snap/{snap_id}")
async def get_snap(
    snap_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> Snap:
    """Gets a snap."""
    snap = await snaps_dao.get_snap_from_id(snap_id)
    if snap:
        (username, fullname) = get_user_info(snap.user_id)

        return Snap(
            id=snap.id,
            author=str(snap.user_id),
            content=snap.content,
            likes=snap.likes,
            shares=snap.shares,
            favs=snap.favs,
            created_at=snap.created_at,
            username=username,
            fullname=fullname,
            parent_id=snap.parent_id,
            visibility=snap.visibility,
        )
    raise HTTPException(status_code=NON_EXISTENT, detail="That tweet doesnt exist")


@router.get("/")
async def get_snaps(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snap ids."""
    my_snaps = []
    users = [user["id"] for user in _followed_users(user_id)]
    users.append(user_id)

    snaps = await snaps_dao.get_from_users(users, limit, offset)
    for a_snap in snaps:

        has_shared = await snaps_dao.user_has_shared(user_id, a_snap.id)
        has_liked = await snaps_dao.user_has_liked(user_id, a_snap.id)

        (username, fullname) = get_user_info(a_snap.user_id)

        my_snaps.append(
            Snap(
                id=a_snap.id,
                author=str(a_snap.user_id),
                content=a_snap.content,
                likes=a_snap.likes,
                shares=a_snap.shares,
                favs=a_snap.favs,
                created_at=a_snap.created_at,
                parent_id=a_snap.parent_id,
                username=username,
                fullname=fullname,
                visibility=a_snap.visibility,
                has_shared=has_shared,
                has_liked=has_liked,
            ),
        )

    return FeedPack(snaps=my_snaps)


@router.get("/snaps_and_shares")
async def get_snaps_and_shares(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snaps and snapshares."""
    snaps = await snaps_dao.get_snaps_and_shares(user_id, limit, offset)
    my_snaps = []
    for a_snap in iter(snaps):
        (username, fullname) = get_user_info(a_snap.user_id)

        user_has_shared = await snaps_dao.user_has_shared(user_id, a_snap.id)
        user_has_liked = await snaps_dao.user_has_liked(user_id, a_snap.id)

        my_snaps.append(
            Snap(
                id=a_snap.id,
                author=str(a_snap.user_id),
                content=a_snap.content,
                likes=a_snap.likes,
                shares=a_snap.shares,
                favs=a_snap.favs,
                created_at=a_snap.created_at,
                parent_id=a_snap.parent_id,
                username=username,
                fullname=fullname,
                visibility=a_snap.visibility,
                has_shared=user_has_shared,
                has_liked=user_has_liked,
            ),
        )
    return FeedPack(snaps=my_snaps)


@router.get("/{user_id}/snaps")
async def get_snaps_from_user(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """
    Returns a list of snap ids.

    WARNING: Does not check if user requested is valid.
    If user does not exist, returns empty list.
    """
    my_snaps = []
    snaps = await snaps_dao.get_from_user(user_id, limit, offset)
    for a_snap in iter(snaps):
        created_at = a_snap.created_at
        (username, fullname) = get_user_info(a_snap.user_id)
        my_snaps.append(
            Snap(
                id=a_snap.id,
                author=a_snap.user_id,
                content=a_snap.content,
                likes=a_snap.likes,
                shares=a_snap.shares,
                favs=a_snap.favs,
                created_at=created_at,
                username=username,
                fullname=fullname,
                parent_id=a_snap.parent_id,
                visibility=a_snap.visibility,
            ),
        )
    return FeedPack(snaps=my_snaps)


def _followed_users(user_id: str) -> List[Dict[str, str]]:
    return httpx.get(_url_get_following(user_id)).json()


def _url_get_following(user_id: str) -> str:
    return f"{settings.identity_socializer_url}/api/interactions/{user_id}/following"


def get_user_info(user_id: str) -> tuple[str, str]:
    """Returns username and fullname of user."""
    try:
        author = httpx.get(_url_get_user(user_id)).json()

        username = author["username"]
        first_name = author["first_name"]
        last_name = author["last_name"]

        fullname = f"{first_name} {last_name}"
        return (username, fullname)
    except Exception:
        return ("Unknown", "Unknown")


def _url_get_user(user_id: str) -> str:
    return f"{settings.identity_socializer_url}/api/auth/users/{user_id}"


@router.get("/get_all_snaps", response_model=None)
async def get_all_snaps(
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> List[SnapsModel]:
    """Returns a list of snaps"""
    return await snaps_dao.get_all_snaps(limit=limit, offset=offset)


@router.get("/get_replies")
async def get_snap_replies(
    snap_id: str,
    user_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snap ids."""
    my_snaps = []

    snaps = await snaps_dao.get_snap_replies(snap_id)

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
