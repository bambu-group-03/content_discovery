import httpx
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from sqlalchemy import inspect

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.settings import settings
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
        created_at=insp.attrs.created_at.value,
    )


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
        return Snap(
            id=snap.id,
            author=str(snap.user_id),
            content=snap.content,
            likes=snap.likes,
            shares=snap.shares,
            favs=snap.favs,
            created_at=snap.created_at,
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

    # TODO: get list of users that user_id follows
    # from different microservice (identity socializer)
    # TEMP:

    # TEMP: dummy ping
    print(f"{settings.identity_socializer_url}/api/echo/")
    response = httpx.post(
        f"{settings.identity_socializer_url}/api/echo/",
        json={"message": f"This is a user: {str(user_id)}"},
    )
    # TODO: parse response into a list of ids
    followed_users = [user_id]
    # message = response.json().get("message")

    for i_d in followed_users:
        snaps = await snaps_dao.get_from_user(user_id, limit, offset)
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
                ),
            )
    return FeedPack(snaps=my_snaps)
