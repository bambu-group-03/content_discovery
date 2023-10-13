from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.snaps_model import SnapsModel


class SnapDAO:
    """Class for accessing snap table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_snaps_model(self,_content: str) -> SnapsModel:
        """
        Add single snap to session.

        :param user_id
        :param content
        """
        snap = SnapsModel(user_id=420,content=_content)
        self.session.add(snap)
        await self.session.flush()
        return snap

    async def get_all_snaps(self, limit: int, offset: int) -> List[SnapsModel]:
        """
        Get all dummy models with limit/offset pagination.

        :param limit: limit of snaps.
        :param offset: offset of snaps.
        :return: stream of snaps.
        """
        raw_snaps = await self.session.execute(
            select(SnapsModel).limit(limit).offset(offset),
        )

        return list(raw_snaps.scalars().fetchall())

    async def filter(
        self,
        id: int,
    ) -> SnapsModel:
        """
        Get specific snap model.

        :param content: content of snap  instance.
        :return: snap models.
        """
        query = select(SnapsModel)
        query = query.where(SnapsModel.id == id)
        rows = await self.session.execute(query)
        return rows.scalars().first()
