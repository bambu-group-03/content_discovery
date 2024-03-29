from typing import Optional

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.share_model import ShareModel
from content_discovery.db.utils import is_valid_uuid


class ShareDAO:
    """Class for accessing shares table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_share_model(
        self,
        user_id: str,
        snap_id: str,
    ) -> Optional[ShareModel]:
        """Add single share to session."""
        try:
            share = ShareModel(user_id=user_id, snap_id=snap_id)

            self.session.add(share)
            await self.session.flush()

            return share
        except Exception:
            return None

    async def delete_share_model(
        self,
        user_id: str,
        snap_id: str,
    ) -> None:
        """Delete single share from session."""
        query = delete(ShareModel).where(
            ShareModel.user_id == user_id,
            ShareModel.snap_id == snap_id,
        )
        await self.session.execute(query)

    async def get_share_model(
        self,
        user_id: str,
        snap_id: str,
    ) -> Optional[ShareModel]:
        """Get single share from session."""
        if not is_valid_uuid(snap_id):
            return None

        query = select(ShareModel).where(
            ShareModel.user_id == user_id,
            ShareModel.snap_id == snap_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
