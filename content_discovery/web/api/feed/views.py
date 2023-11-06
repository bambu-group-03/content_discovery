from typing import Any, List, Optional

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
        user = httpx.get(_url_get_user(snap.user_id)).json()
        return Snap(
            id=snap.id,
            author=str(snap.user_id),
            content=snap.content,
            likes=snap.likes,
            shares=snap.shares,
            favs=snap.favs,
            created_at=snap.created_at,
            username=user["username"],
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
    # TODO: parse response into a list of ids

    for user in _users_followed_by(user_id):
        snaps = await snaps_dao.get_from_user(user["id"], limit, offset)
        for a_snap in iter(snaps):
            an_author = _get_username(user_id)
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
                    username=an_author,
                    visibility=a_snap.visibility,
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
        an_author = _get_username(user_id)
        my_snaps.append(
            Snap(
                id=a_snap.id,
                author=a_snap.user_id,
                content=a_snap.content,
                likes=a_snap.likes,
                shares=a_snap.shares,
                favs=a_snap.favs,
                created_at=created_at,
                username=an_author,
                parent_id=a_snap.parent_id,
                visibility=a_snap.visibility,
            ),
        )
    return FeedPack(snaps=my_snaps)


async def _get_snaps_from_users(
    following: Any,
    snaps_dao: SnapDAO,
    limit: int,
    offset: int,
) -> Optional[list[Snap]]:
    my_snaps: List[Snap] = []
    for user in following:
        snaps = await snaps_dao.get_from_user(user["id"], limit, offset)
        for a_snap in iter(snaps):
            created_at = a_snap.created_at
            print(created_at.__class__)
            my_snaps.append(
                Snap(
                    id=a_snap.id,
                    author=str(a_snap.user_id),
                    content=a_snap.content,
                    likes=a_snap.likes,
                    shares=a_snap.shares,
                    favs=a_snap.favs,
                    created_at=created_at,
                    username=user["username"],
                    parent_id=a_snap.parent_id,
                    visibility=a_snap.visibility,
                ),
            )
    return my_snaps


def _users_followed_by(user_id: str) -> list[Any]:
    response = httpx.get(_url_get_following(user_id))
    if response.status_code != OK:
        raise ValueError("Bad request to id socializer", str(response))
    return response.json()


def _url_get_following(user_id: str) -> str:
    return f"{settings.identity_socializer_url}/api/auth/{user_id}/following"


def _get_username(user_id: str) -> str:
    author = httpx.get(_url_get_user(user_id)).json()
    if not author:
        return author
    return author["username"]


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
