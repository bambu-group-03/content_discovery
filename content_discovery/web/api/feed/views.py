import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends

from content_discovery.constants import Frequency, Privacy
from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.mention_dao import MentionDAO
from content_discovery.db.dao.snaps_dao import SnapDAO, sort_snaps_with_children
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.notifications import Notifications
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
    generate_freqencies,
    get_user_info,
)

router = APIRouter()

NON_EXISTENT = 405
BAD_INPUT = 214
OK = 200
DAYS_MONTH = 30


async def create_tweet(snap, user_id, hashtag_dao, mention_dao, snaps_dao):
    # Create hashtags and mentions
    await hashtag_dao.create_hashtags(snap.id, snap.content)
    await mention_dao.create_mentions(snap.id, snap.content)
    mentions = await mention_dao.get_mentioned_users_in_snap(snap.id)
    mentions_ids = [mention.mentioned_id for mention in mentions]
    unique = list(dict.fromkeys(mentions_ids))
    for mention_id in unique:
        await Notifications().send_mention_notification(
            from_id=user_id,
            to_id=mention_id,
            snap_id=snap.id,
            snap_dao=snaps_dao,
        )
    completed_snaps = await complete_snaps([snap], user_id, snaps_dao)
    return completed_snaps.snaps[0]


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
    return await create_tweet(
        snap,
        incoming_message.user_id,
        hashtag_dao, mention_dao, snaps_dao)


@router.post("/reply", response_model=None)
async def reply_snap(
    incoming_message: ReplySnap,
    snaps_dao: SnapDAO = Depends(),
    hashtag_dao: HashtagDAO = Depends(),
    mention_dao: MentionDAO = Depends(),
) -> Optional[SnapsModel]:
    """Create a reply snap with the received content."""
    if not incoming_message.parent_id:
        raise HTTPException(400, detail="Must specify parent tweet")

    snap = await snaps_dao.create_reply_snap(
        user_id=incoming_message.user_id,
        content=incoming_message.content,
        parent_id=incoming_message.parent_id,
        privacy=incoming_message.privacy,
    )

    return await create_tweet(
        snap,
        incoming_message.user_id,
        hashtag_dao, mention_dao, snaps_dao)


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
    completed_snaps = await complete_snaps_and_shares(snaps, user_id, snaps_dao)

    if completed_snaps.snaps is not None:
        return sort_snaps_with_children(completed_snaps.snaps)
    return FeedPack(snaps=[])


@router.get("/{user_id}/snaps_and_shares/requested_by/{requester_id}")
async def get_snaps_and_shares(
    user_id: str,
    requester_id: str,
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snaps and snapshares from user."""
    try:
        followed_by_user = followed_users(requester_id)
    except:
        raise HTTPException(status_code=500, detail="Could not find requester")
    snaps = await snaps_dao.get_snaps_and_shares(
        [{"id": user_id}],
        followed_by_user,
        limit,
        offset,
    )

    return await complete_snaps_and_shares(
        snaps,
        requester_id,
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


@router.get("/admin/{user_id}/snaps")
async def get_snaps_from_user_by_admin(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snap ids from user by admin."""
    snaps = []

    snap_models = await snaps_dao.get_from_user_by_admin(user_id, limit, offset)
    for snap_model in snap_models:
        (username, fullname, url) = get_user_info(snap_model.user_id)

        snap = Snap(
            id=snap_model.id,
            author=snap_model.user_id,
            content=snap_model.content,
            likes=snap_model.likes,
            shares=snap_model.shares,
            favs=snap_model.favs,
            created_at=snap_model.created_at,
            username=username,
            fullname=fullname,
            parent_id=snap_model.parent_id,
            visibility=snap_model.visibility,
            privacy=snap_model.privacy,
        )

        snaps.append(snap)

    return FeedPack(snaps=snaps)


@router.get("/get_all_snaps", response_model=None)
async def get_all_snaps(
    limit: int = 10,
    offset: int = 0,
    snaps_dao: SnapDAO = Depends(),
) -> List[Any]:
    """Returns a list of snaps"""
    completed_snap = []
    snaps = await snaps_dao.get_all_snaps(limit=limit, offset=offset)

    for snap in snaps:
        (username, fullname, url) = get_user_info(snap.user_id)

        completed_snap.append(
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

    return completed_snap


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

    time_units = {
        Frequency.hourly: datetime.timedelta(hours=1),
        Frequency.daily: datetime.timedelta(days=1),
        Frequency.per_minute: datetime.timedelta(minutes=1),
    }

    time_unit = time_units[frequency]

    snapcounts = []
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


@router.get("/snaps/stats/monthly_frequency")
async def get_snap_frequencies_redefinition(
    snaps_dao: SnapDAO = Depends(),
) -> Any:
    """Returns snaps created in recent months."""
    dict_dates = await generate_freqencies(
        snaps_dao,
        datetime.timedelta(days=DAYS_MONTH),
        5,
    )
    return_list = []
    for date, count in dict_dates.items():
        return_list.append({"month": date, "value": str(count)})
    return return_list
