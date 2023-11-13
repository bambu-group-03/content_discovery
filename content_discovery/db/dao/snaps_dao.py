import uuid
from typing import Any, List, Optional, Union

from fastapi import Depends
from sqlalchemy import delete, or_, outerjoin, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from content_discovery.constants import Visibility
from content_discovery.db.dependencies import get_db_session
from content_discovery.db.models.fav_model import FavModel
from content_discovery.db.models.hashtag_model import HashtagModel
from content_discovery.db.models.like_model import LikeModel
from content_discovery.db.models.mention_model import MentionModel
from content_discovery.db.models.share_model import ShareModel
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

    async def create_reply_snap(
        self,
        user_id: str,
        content: str,
        parent_id: str,
    ) -> Optional[SnapsModel]:
        """Add reply snap to session."""
        try:
            snap = SnapsModel(user_id=user_id, content=content, parent_id=parent_id)

            self.session.add(snap)
            await self.session.flush()

            return snap
        except Exception:
            return None

    async def update_snap(
        self,
        user_id: str,
        snap_id: str,
        content: str,
    ) -> None:
        """Update single snap to session."""
        if not is_valid_uuid(snap_id):
            return

        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .where(SnapsModel.user_id == user_id)
            .values(
                content=content,
            )
        )

        await self.session.execute(stmt)

    async def delete_snap(
        self,
        snap_id: str,
    ) -> None:
        """
        Delete given snap and its interactions.

        :param user_id
        """
        if not is_valid_uuid(snap_id):
            return

        # Delete snap likes
        await self.delete_snap_likes(snap_id=snap_id)

        # Delete snap shares
        await self.delete_snap_shares(snap_id)

        # Delete snap favs
        await self.delete_snap_favs(snap_id)

        # Delete snap hashtags
        await self.delete_snap_hashtags(snap_id)

        # Delete snap mentions
        await self.delete_snap_mentions(snap_id)

        query = delete(SnapsModel).where(SnapsModel.id == snap_id)
        await self.session.execute(query)

    async def delete_snap_likes(
        self,
        snap_id: str,
    ) -> None:
        """Delete specific snap likes."""
        query = delete(LikeModel).where(LikeModel.snap_id == snap_id)
        await self.session.execute(query)

    async def delete_snap_shares(
        self,
        snap_id: str,
    ) -> None:
        """Delete specific snap shares."""
        query = delete(ShareModel).where(ShareModel.snap_id == snap_id)
        await self.session.execute(query)

    async def delete_snap_favs(
        self,
        snap_id: str,
    ) -> None:
        """Delete specific snap favs."""
        query = delete(FavModel).where(FavModel.snap_id == snap_id)
        await self.session.execute(query)

    async def delete_snap_hashtags(
        self,
        snap_id: str,
    ) -> None:
        """Delete specific snap hashtags."""
        query = delete(HashtagModel).where(HashtagModel.snap_id == snap_id)
        await self.session.execute(query)

    async def delete_snap_mentions(
        self,
        snap_id: str,
    ) -> None:
        """Delete specific snap mentions."""
        query = delete(MentionModel).where(MentionModel.snap_id == snap_id)
        await self.session.execute(query)

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

    async def get_from_users(
        self,
        users: list[str],
        limit: int,
        offset: int,
    ) -> list[SnapsModel]:
        """
        Get snaps from a set of users.

        :param user_id:
        :param limit: up to ho many snaps to get
        :param offset: from where to begin providing results
        """
        query = select(SnapsModel)
        query = query.where(SnapsModel.visibility == Visibility.PUBLIC.value)
        query = query.where(SnapsModel.user_id.in_(users))
        query = query.order_by(SnapsModel.created_at.desc())
        query = query.limit(limit).offset(offset)

        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

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
        query = query.where(SnapsModel.visibility == Visibility.PUBLIC.value)
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

    async def make_public(
        self,
        snap_id: str,
    ) -> None:
        """Set visibility to public"""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                visibility=Visibility.PUBLIC.value,
            )
        )

        await self.session.execute(stmt)

    async def make_private(
        self,
        snap_id: str,
    ) -> None:
        """Set visibility to private"""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                visibility=Visibility.PRIVATE.value,
            )
        )

        await self.session.execute(stmt)

    async def filter_snaps(
        self,
        content: str,
    ) -> List[SnapsModel]:
        """Get list of filtered snaps by content."""
        query = select(SnapsModel).distinct()
        query = query.where(SnapsModel.visibility == Visibility.PUBLIC.value)
        query = query.filter(SnapsModel.content.ilike(f"%{content}%"))

        rows = await self.session.execute(query)

        return list(rows.scalars().fetchall())

    async def get_snaps_and_shares(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> List[SnapsModel]:
        """Get snaps shared by a user along with snaps written by a user"""
        joined = outerjoin(SnapsModel, ShareModel, SnapsModel.id == ShareModel.snap_id)
        selected = joined.select()
        filter1 = selected.where(
            or_(SnapsModel.user_id == user_id, ShareModel.user_id == user_id),
        )
        query = filter1.order_by(
            coalesce(SnapsModel.created_at, ShareModel.created_at).desc(),
        )
        rows = await self.session.execute(query.limit(limit).offset(offset))
        return list(rows.scalars().fetchall())

    async def user_has_shared(self, user_id: str, snap_id: uuid.UUID) -> bool:
        """Boolean whether user has shared the snap"""
        query = select(ShareModel)
        query = query.where(ShareModel.snap_id == snap_id).where(
            ShareModel.user_id == user_id,
        )
        rows = await self.session.execute(query)
        my_list = list(rows.scalars().fetchall())

        return bool(my_list)

    async def user_has_liked(self, user_id: str, snap_id: uuid.UUID) -> bool:
        """Boolean whether user has liked the snap"""
        query = select(LikeModel)
        query = query.where(LikeModel.snap_id == snap_id).where(
            LikeModel.user_id == user_id,
        )

        rows = await self.session.execute(query)
        my_list = list(rows.scalars().fetchall())

        return bool(my_list)

    async def get_snap_replies(self, snap_id: str) -> List[SnapsModel]:
        """Get replies to a snap"""
        if not is_valid_uuid(snap_id):
            return []

        query = select(SnapsModel)
        query = query.where(SnapsModel.visibility == Visibility.PUBLIC.value)
        query = query.where(SnapsModel.parent_id == snap_id)
        rows = await self.session.execute(query)

        return list(rows.scalars().fetchall())

    async def count_replies_by_snap(self, snap_id: Any) -> int:
        """Get number of replies of snap_id"""
        replies = await self.get_snap_replies(snap_id)

        return len(replies)
