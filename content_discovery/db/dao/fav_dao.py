from typing import List, Optional

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.fav_model import FavModel
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.db.utils import is_valid_uuid


class FavDAO:
    """Class for accessing favs table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_fav_model(self, user_id: str, snap_id: str) -> Optional[FavModel]:
        """Add single fav to session."""
        try:
            fav = FavModel(user_id=user_id, snap_id=snap_id)

            self.session.add(fav)
            await self.session.flush()

            return fav
        except Exception:
            return None

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

    async def get_fav_model(
        self,
        user_id: str,
        snap_id: str,
    ) -> Optional[FavModel]:
        """Get single fav from session."""
        if not is_valid_uuid(snap_id):
            return None

        query = select(FavModel).where(
            FavModel.user_id == user_id,
            FavModel.snap_id == snap_id,
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_favs_by_user(
        self,
        user_id: str,
    ) -> List[SnapsModel]:
        """Get favs by user from session."""
        query = select(SnapsModel)
        query = query.join(FavModel)
        query = query.where(FavModel.user_id == user_id)

        result = await self.session.execute(query)

        return list(result.scalars().fetchall())
