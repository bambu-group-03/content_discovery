from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.mention_dao import MentionDAO
from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.web.api.feed.schema import (
    FeedPack,
    PostSnap,
    ReplySnap,
    Snap,
    UpdateSnap,
)
from content_discovery.web.api.utils import (
    complete_snap,
    complete_snaps,
    complete_snaps_and_shares,
    followed_users,
)

router = APIRouter()

NON_EXISTENT = 405
OK = 200


@router.post("/post", response_model=None)
async def post_snap(
    incoming_message: PostSnap,
    snaps_dao: SnapDAO = Depends(),
    hashtag_dao: HashtagDAO = Depends(),
    mention_dao: MentionDAO = Depends(),
) -> Optional[SnapsModel]:
    """Create a snap with the received content."""
    snap = await snaps_dao.create_snaps_model(
        user_id=incoming_message.user_id,
        content=incoming_message.content,
    )

    # Create hashtags and mentions
    await hashtag_dao.create_hashtags(snap.id, snap.content)
    await mention_dao.create_mentions(snap.id, snap.content)

    return snap


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
    user_id: str,
    snap_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> Snap:
    """Gets a snap."""
    snap = await snaps_dao.get_snap_from_id(snap_id)

    if snap:
        return await complete_snap(snap, user_id, snaps_dao)

    raise HTTPException(status_code=NON_EXISTENT, detail="That tweet doesnt exist")


@router.get("/")
async def get_snaps(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snaps shared or written by the user's followed."""
    users = [user["id"] for user in followed_users(user_id)]
    users.append(user_id)

    snaps = await snaps_dao.get_snaps_and_shares(users, limit, offset)
    return await complete_snaps_and_shares(
        snaps,
        user_id,
        snaps_dao,
    )


@router.get("/{user_id}/snaps_and_shares")
async def get_snaps_and_shares(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snaps and snapshares from user."""
    snaps = await snaps_dao.get_snaps_and_shares(
        [user_id],
        limit,
        offset,
    )
    return await complete_snaps_and_shares(
        snaps,
        user_id,
        snaps_dao,
    )


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
    snaps = await snaps_dao.get_from_user(user_id, limit, offset)

    return await complete_snaps(snaps, user_id, snaps_dao)


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
    """Returns a list of replies of a snap ids."""
    snaps = await snaps_dao.get_snap_replies(snap_id)

    return await complete_snaps(snaps, user_id, snaps_dao)
