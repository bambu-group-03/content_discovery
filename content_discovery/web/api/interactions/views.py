from fastapi import APIRouter
from fastapi.param_functions import Depends
from content_discovery.db.dao.like_dao import LikeDAO

router = APIRouter()

@router.post("/{user_id}/like/{snap_id}")
async def like_snap(
    user_id: str,
    snap_id: str,
    like_dao: LikeDAO = Depends(),
) -> None:
    """ User likes a snap."""
    await like_dao.create_like_model(user_id=user_id, snap_id=snap_id)

@router.delete("/{user_id}/unlike/{snap_id}")
async def unlike_snap(
    user_id: str,
    snap_id: str,
    like_dao: LikeDAO = Depends(),
) -> None:
    """ User unlikes a snap."""
    await like_dao.delete_like_model(user_id=user_id, snap_id=snap_id)
