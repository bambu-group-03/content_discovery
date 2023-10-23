from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from sqlalchemy import inspect

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.web.api.feed.schema import FeedPack, PostSnap, Snap

router = APIRouter()

NON_EXISTENT = 405


@router.post("/post")
async def post_snap(
    incoming_message: PostSnap,
    snaps_dao: SnapDAO = Depends(),
) -> Snap:
    """Uploads a snap with the received content."""
    snap = await snaps_dao.create_snaps_model(
        user_id=incoming_message.user_id,
        content=incoming_message.content,
    )
    insp = inspect(snap)
    i_d = insp.attrs.id.value
    return Snap(
        id=i_d,
        author=str(insp.attrs.user_id.value),
        content=insp.attrs.content.value,
        likes=insp.attrs.likes.value,
        shares=insp.attrs.shares.value,
        favs=insp.attrs.favs.value,
    )


@router.get("/snap/{snap_id}")
async def get_snap(
    snap_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> Snap:
    """Gets a snap."""
    snap = await snaps_dao.get_snap_from_id(snap_id)
    if snap:
        return Snap(
            id=snap.id,
            author=str(snap.user_id),
            content=snap.content,
            likes=snap.likes,
            shares=snap.shares,
            favs=snap.favs,
        )
    raise HTTPException(status_code=NON_EXISTENT, detail="That tweet doesnt exist")


@router.get("/")
async def get_snaps(
    user_id: str,
    snaps_dao: SnapDAO = Depends(),
) -> FeedPack:
    """Returns a list of snap ids."""
    my_snaps = []

    # TODO: get list of users that user_id follows
    # from different microservice (identity socializer)
    # TEMP:
    followed_users = [user_id]
    for i_d in followed_users:
        snaps = await snaps_dao.get_from_user(i_d, 100, 0)
        for snap in iter(snaps):
            my_snaps.append(
                Snap(
                    id=snap.id,
                    author=str(snap.user_id),
                    content=snap.content,
                    likes=snap.likes,
                    shares=snap.shares,
                    favs=snap.favs,
                ),
            )
    return FeedPack(snaps=my_snaps)
