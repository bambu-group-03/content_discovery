from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.like_model import LikeModel


class LikeDAO:
    """Class for accessing likes table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_like_model(self, user_id: str, snap_id: str) -> None:
        """ Add single like to session. """
        self.session.add(LikeModel(user_id=user_id, snap_id=snap_id))

    async def delete_like_model(
        self,
        user_id: str, snap_id: str
    ) -> None:
        """Delete single like from session."""
        query = delete(LikeModel).where(
            LikeModel.user_id == user_id,
            LikeModel.snap_id == snap_id,
        )
        await self.session.execute(query)