import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends

from content_discovery.constants import Frequency, Privacy
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
BAD_INPUT = 214
OK = 200


@router.post("/post", response_model=None)
async def post_snap(
    incoming_message: PostSnap,
    snaps_dao: SnapDAO = Depends(),
    hashtag_dao: HashtagDAO = Depends(),
    mention_dao: MentionDAO = Depends(),
) -> Optional[SnapsModel]:
    """Create a snap with the received content."""
    Privacy.validate(incoming_message.privacy)
    # create snap
    snap = await snaps_dao.create_snaps_model(
        user_id=incoming_message.user_id,
        content=incoming_message.content,
        privacy=incoming_message.privacy,
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
        privacy=incoming_message.privacy,
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
    users = followed_users(user_id)
    snaps = await snaps_dao.get_snaps_and_shares(users, users, limit, offset)
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
    followed_by_user = followed_users(user_id)
    snaps = await snaps_dao.get_snaps_and_shares(
        [{"id": user_id}],
        followed_by_user,
        limit,
        offset,
    )

    return await complete_snaps_and_shares(
        snaps,
        user_id,
        snaps_dao,
    )


@router.get("/{user_id}/shares")
async def get_shares(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snaps and snapshares from user."""
    snaps = await snaps_dao.get_shared_snaps(
        [user_id],
        limit,
        offset,
    )
    return await complete_snaps(
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
    followed = followed_users(user_id)
    snaps = await snaps_dao.get_from_user(user_id, followed, limit, offset)
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
    followed = followed_users(user_id)
    snaps = await snaps_dao.get_snap_replies(snap_id, followed)

    return await complete_snaps(snaps, user_id, snaps_dao)


# TODO: mover a metricas


@router.get("/snaps/stats/start/{start_datetime}/end/{end_datetime}")
async def get_snap_count(
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
    snaps_dao: SnapDAO = Depends(),
) -> int:
    """Returns number of snaps created in a time period."""
    snapcounts = await snaps_dao.quantity_new_snaps_in_time_period(
        start_datetime,
        end_datetime,
    )
    print(snapcounts)
    return snapcounts


@router.get("/snaps/stats/frequency/{frequency}/number_of_points/{number}")
async def get_snap_frequencies(
    frequency: Frequency,
    number: int,
    snaps_dao: SnapDAO = Depends(),
) -> List[int]:
    """Returns number of snaps created in a time period."""
    if number <= 0:
        raise HTTPException(status_code=BAD_INPUT, detail="Bad input")

    snapcounts = []

    if frequency is Frequency.hourly:
        time_unit = datetime.timedelta(hours=1)
    if frequency is Frequency.daily:
        time_unit = datetime.timedelta(days=1)
    if frequency is Frequency.per_minute:
        time_unit = datetime.timedelta(minutes=1)
    start_datetime = datetime.datetime.utcnow() - (time_unit * number)
    for _ in range(0, number):
        end_datetime = start_datetime + time_unit
        print(start_datetime)
        print(end_datetime)
        count = await snaps_dao.quantity_new_snaps_in_time_period(
            start_datetime,
            end_datetime,
        )
        snapcounts.append(count)
        start_datetime = end_datetime
    print(snapcounts)
    return snapcounts
