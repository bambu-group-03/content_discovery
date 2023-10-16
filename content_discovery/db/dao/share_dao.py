from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.share_model import ShareModel

class ShareModel:
    """Class for accessing shares table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_share_model(self, user_id: str, snap_id: str) -> None:
        """ Add single share to session. """
        self.session.add(ShareModel(user_id=user_id, snap_id=snap_id))

    async def delete_share_model(
        self,
        user_id: str, snap_id: str
    ) -> None:
        """Delete single share from session."""
        query = delete(ShareModel).where(
            ShareModel.user_id == user_id,
            ShareModel.snap_id == snap_id,
        )
        await self.session.execute(query)