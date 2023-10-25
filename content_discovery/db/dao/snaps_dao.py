from typing import List, Union

from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.snaps_model import SnapsModel
from content_discovery.db.utils import is_valid_uuid


class SnapDAO:
    """Class for accessing snap table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_snaps_model(self, user_id: str, content: str) -> SnapsModel:
        """
        Add single snap to session.

        :param user_id
        :param content
        """
        snap = SnapsModel(user_id=user_id, content=content)
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

    async def get_snap_from_id(
        self,
        snap_id: str,
    ) -> Union[SnapsModel, None]:
        """Get specific snap model."""
        if not is_valid_uuid(snap_id):
            return None

        query = select(SnapsModel).where(SnapsModel.id == snap_id)
        rows = await self.session.execute(query)
        return rows.scalars().first()

    async def delete(
        self,
        snap_id: str,
    ) -> Union[SnapsModel, None]:
        """Get specific snap model."""
        if not is_valid_uuid(snap_id):
            return None

        query = delete(SnapsModel).where(SnapsModel.id == snap_id)
        await self.session.execute(query)


    async def get_from_user(
        self,
        user_id: str,
        limit: int,
        offset: int,
    ) -> list[SnapsModel]:
        """
        Get specific snap model from user.

        :param user_id:
        :param limit: up to ho many snaps to get
        :param offset: from where to begin providing results
        """
        query = select(SnapsModel)
        query = query.where(SnapsModel.user_id == user_id)
        query = query.limit(limit).offset(offset)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def increase_likes(
        self,
        snap_id: str,
    ) -> None:
        """Increase likes counter."""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                likes=SnapsModel.likes + 1,
            )
        )

        await self.session.execute(stmt)

    async def decrease_likes(
        self,
        snap_id: str,
    ) -> None:
        """Decrease likes counter."""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                likes=SnapsModel.likes - 1,
            )
        )

        await self.session.execute(stmt)

    async def increase_shares(
        self,
        snap_id: str,
    ) -> None:
        """Increase shares counter."""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                shares=SnapsModel.shares + 1,
            )
        )

        await self.session.execute(stmt)

    async def decrease_shares(
        self,
        snap_id: str,
    ) -> None:
        """Decrease shares counter."""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                shares=SnapsModel.shares - 1,
            )
        )

        await self.session.execute(stmt)

    async def increase_favs(
        self,
        snap_id: str,
    ) -> None:
        """Increase favs counter."""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                favs=SnapsModel.favs + 1,
            )
        )

        await self.session.execute(stmt)

    async def decrease_favs(
        self,
        snap_id: str,
    ) -> None:
        """Decrease favs counter."""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                favs=SnapsModel.favs - 1,
            )
        )

        await self.session.execute(stmt)
