from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.fav_model import FavModel


class FavDAO:
    """Class for accessing favs table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_fav_model(self, user_id: str, snap_id: str) -> None:
        """Add single fav to session."""
        self.session.add(FavModel(user_id=user_id, snap_id=snap_id))

    async def delete_fav_model(
        self,
        user_id: str,
        snap_id: str,
    ) -> None:
        """Delete single fav from session."""
        query = delete(FavModel).where(
            FavModel.user_id == user_id,
            FavModel.snap_id == snap_id,
        )
        await self.session.execute(query)
