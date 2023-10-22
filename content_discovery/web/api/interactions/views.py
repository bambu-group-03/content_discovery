from fastapi import APIRouter
from fastapi.param_functions import Depends

from content_discovery.db.dao.fav_dao import FavDAO
from content_discovery.db.dao.like_dao import LikeDAO
from content_discovery.db.dao.share_dao import ShareDAO
from content_discovery.db.dao.snaps_dao import SnapDAO

router = APIRouter()


@router.post("/{user_id}/like/{snap_id}")
async def like_snap(
    user_id: str,
    snap_id: str,
    like_dao: LikeDAO = Depends(),
    snap_dao: SnapDAO = Depends(),
) -> None:
    """User likes a snap."""
    snap = await snap_dao.get_snap_from_id(snap_id)

    if not snap:
        return

    like = await like_dao.create_like_model(user_id=user_id, snap_id=snap_id)

    if not like:
        return

    await snap_dao.update_likes(snap_id=snap_id, updated_likes=snap.likes + 1)


@router.delete("/{user_id}/unlike/{snap_id}")
async def unlike_snap(
    user_id: str,
    snap_id: str,
    like_dao: LikeDAO = Depends(),
) -> None:
    """User unlikes a snap."""
    await like_dao.delete_like_model(user_id=user_id, snap_id=snap_id)


@router.post("/{user_id}/share/{snap_id}")
async def share_snap(
    user_id: str,
    snap_id: str,
    share_dao: ShareDAO = Depends(),
) -> None:
    """User shares a snap."""
    await share_dao.create_share_model(user_id=user_id, snap_id=snap_id)


@router.delete("/{user_id}/unshare/{snap_id}")
async def unshare_snap(
    user_id: str,
    snap_id: str,
    share_dao: ShareDAO = Depends(),
) -> None:
    """User unfav a snap."""
    await share_dao.delete_share_model(user_id=user_id, snap_id=snap_id)


@router.post("/{user_id}/fav/{snap_id}")
async def fav_snap(
    user_id: str,
    snap_id: str,
    fav_dao: FavDAO = Depends(),
) -> None:
    """User favs a snap."""
    await fav_dao.create_fav_model(user_id=user_id, snap_id=snap_id)


@router.delete("/{user_id}/unfav/{snap_id}")
async def unfav_snap(
    user_id: str,
    snap_id: str,
    fav_dao: FavDAO = Depends(),
) -> None:
    """User unfav a snap."""
    await fav_dao.delete_fav_model(user_id=user_id, snap_id=snap_id)
