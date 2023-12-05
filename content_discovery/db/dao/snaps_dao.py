import datetime
import uuid
from typing import Any, Dict, List, Optional, Union

from fastapi import Depends
from sqlalchemy import Select, delete, func, or_, outerjoin, select, update
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from content_discovery.constants import Privacy, Visibility
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

    async def create_snaps_model(
        self,
        user_id: str,
        content: str,
        privacy: int,
    ) -> SnapsModel:
        """
        Add single snap to session.

        :param user_id
        :param content
        :param privacy
        """
        snap = SnapsModel(user_id=user_id, content=content, privacy=privacy)
        self.session.add(snap)
        await self.session.flush()
        return snap

    async def create_reply_snap(
        self,
        user_id: str,
        content: str,
        parent_id: str,
        privacy: int,
    ) -> Optional[SnapsModel]:
        """Add reply snap to session."""
        snap = SnapsModel(
            user_id=user_id,
            content=content,
            parent_id=parent_id,
            privacy=privacy,
        )
        self.session.add(snap)
        await self.session.flush()
        return snap

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
        Get all snaps models with limit/offset pagination.

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

    async def get_from_user(
        self,
        user_id: str,
        requester_is_following: List[Dict[str, str]],
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
        query = _query_visibility_is_public(query)
        query = _query_privacy_filter_to_only_followers(query, requester_is_following)
        query = query.where(SnapsModel.user_id == user_id)
        query = query.limit(limit).offset(offset)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def get_from_user_by_admin(
        self,
        user_id: str,
        limit: int,
        offset: int,
    ) -> list[SnapsModel]:
        """Get snaps from user by admin"""
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

    async def make_public(
        self,
        snap_id: str,
    ) -> None:
        """Set visibility to public"""
        stmt = (
            update(SnapsModel)
            .where(SnapsModel.id == snap_id)
            .values(
                visibility=_default_visibility(),
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
                visibility=_private_visibility(),
            )
        )

        await self.session.execute(stmt)

    async def filter_snaps(
        self,
        content: str,
        requester_is_following: List[Dict[str, str]],
    ) -> List[SnapsModel]:
        """Get list of filtered snaps by content."""
        query = select(SnapsModel).distinct()
        query = _query_visibility_is_public(query)
        query = _query_privacy_filter_to_only_followers(query, requester_is_following)
        query = query.filter(SnapsModel.content.ilike(f"%{content}%"))

        rows = await self.session.execute(query)

        return list(rows.scalars().fetchall())

    async def admin_filter_snaps(
        self,
        content: str,
    ) -> List[SnapsModel]:
        """Get list of filtered snaps by content."""
        query = select(SnapsModel)
        query = query.filter(SnapsModel.content.ilike(f"%{content}%"))

        rows = await self.session.execute(query)

        return list(rows.scalars().fetchall())

    async def get_shared_snaps(
        self,
        user_ids: List[str],
        limit: int = 10,
        offset: int = 0,
    ) -> List[SnapsModel]:
        """

        Get snaps shared by a user in 'user_ids'

        Used for constructing the snapshare history.
        TODO: what happens if you share a snap and then it's made private?

        """
        joined = outerjoin(SnapsModel, ShareModel, SnapsModel.id == ShareModel.snap_id)
        selected = joined.select()
        relevant_snaps = selected.where(
            or_(
                ShareModel.user_id.in_(user_ids),
            ),
        )
        query = relevant_snaps.order_by(
            coalesce(SnapsModel.created_at, ShareModel.created_at).desc(),
        )

        query = _query_visibility_is_public(query)
        result = await self.session.execute(query.limit(limit).offset(offset))
        return list(result.scalars().fetchall())

    async def get_snaps_and_shares(
        self,
        users: List[Dict[str, str]],
        requester_is_following: List[Dict[str, str]],
        limit: int = 10,
        offset: int = 0,
    ) -> List[RowMapping]:
        """
        Get snaps written or shared by a user in 'users'

        Used for constructing a feed.
        If the snap was shared, include who shared it.
        For every RowMapping, you may access the snap data
        using snap["SnapsModel"].a_snap_attribute
        and the share data using snap["ShareModel"].a_share_attribute
        """
        joined = outerjoin(SnapsModel, ShareModel, SnapsModel.id == ShareModel.snap_id)
        selected = joined.select()
        user_ids = [_dict["id"] for _dict in users]
        query = selected.where(
            or_(
                SnapsModel.user_id.in_(user_ids),
                ShareModel.user_id.in_(user_ids),
            ),
        )
        query = _query_privacy_filter_to_only_followers(query, requester_is_following)
        query = query.order_by(
            coalesce(ShareModel.created_at, SnapsModel.created_at).desc(),
        )

        result = await self.session.execute(query.limit(limit).offset(offset))
        return list(result.mappings().fetchall())

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

    async def user_has_faved(self, user_id: str, snap_id: uuid.UUID) -> bool:
        """Boolean whether user has faved the snap"""
        query = select(FavModel)
        query = query.where(FavModel.snap_id == snap_id)
        query = query.where(FavModel.user_id == user_id)

        rows = await self.session.execute(query)
        res = list(rows.scalars().fetchall())

        return bool(res)

    # codigo repetido - uno filtra privacidad y otro no

    async def get_snap_replies(
        self,
        snap_id: str,
        requester_is_following: List[Dict[str, str]],
    ) -> List[SnapsModel]:
        """Get replies to a snap"""
        if not is_valid_uuid(snap_id):
            return []

        query = select(SnapsModel)
        query = _query_visibility_is_public(query)
        query = _query_privacy_filter_to_only_followers(query, requester_is_following)
        query = query.where(SnapsModel.parent_id == snap_id)
        rows = await self.session.execute(query)

        return list(rows.scalars().fetchall())

    async def count_replies_by_snap(self, snap_id: Any) -> int:
        """Get number of replies of snap_id"""
        if not is_valid_uuid(snap_id):
            raise ValueError("bad UUID")

        query = select(SnapsModel)
        query = query.where(SnapsModel.parent_id == snap_id)
        rows = await self.session.execute(query)
        return len(list(rows.scalars().fetchall()))

    async def quantity_new_snaps_in_time_period(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        filter_only_public: bool = False,
    ) -> int:
        """Get number of snaps in the given timeframe"""
        start = start.replace(tzinfo=None)
        end = end.replace(tzinfo=None)
        query = select(func.count("*").label("count"))
        query = query.where(SnapsModel.created_at > start)
        query = query.where(SnapsModel.created_at < end)
        if filter_only_public:
            query = _query_privacy_is_public(query)
        rows = await self.session.execute(query)
        count = rows.scalars().first()
        return count if count else 0

    async def get_snap_metrics_by_user(
        self,
        user_id: str,
        start_date: str,
        end_date: str,
    ) -> Any:
        """Get snap metrics by user in a given timeframe"""
        try:
            start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return []

        res = await self.session.execute(
            select(SnapsModel).where(SnapsModel.user_id == user_id),
        )

        snaps_by_user = res.scalars().fetchall()

        total_snaps = len(snaps_by_user)
        total_likes = 0
        total_shares = 0

        for snap_by_user in snaps_by_user:
            total_likes += snap_by_user.likes
            total_shares += snap_by_user.shares

        snaps_in_period = list(
            filter(
                lambda snap: snap.created_at >= start and snap.created_at <= end,
                snaps_by_user,
            ),
        )

        period_snap = len(snaps_in_period)
        period_like = 0
        period_share = 0

        for snap_in_period in snaps_in_period:
            period_like += snap_in_period.likes
            period_share += snap_in_period.shares

        return [
            {
                "total_snaps": total_snaps,
                "total_likes": total_likes,
                "total_shares": total_shares,
                "period_snaps": period_snap,
                "period_likes": period_like,
                "period_shares": period_share,
            },
        ]


def _query_visibility_is_public(query: Any) -> Any:
    """Snap visibility is public"""
    return query.where(SnapsModel.visibility == Visibility.PUBLIC.value)


def _query_privacy_is_public(query: Any) -> Any:
    """Snap privacy is public"""
    return query.where(SnapsModel.privacy == Privacy.PUBLIC.value)


def _default_visibility() -> int:
    return Visibility.PUBLIC.value


def _private_visibility() -> int:
    return Visibility.PRIVATE.value


def _query_privacy_filter_to_only_followers(
    query: Select[tuple[SnapsModel]],
    requester_is_following: List[Dict[str, str]],
) -> Select[tuple[SnapsModel]]:
    """
    Get query expression for: snap.privacy = 1 OR snap.user_id IN [followed1, followed2]

    this function pings identity socializer to resolve followed users
    """
    followed_by_user_list = [_dict["id"] for _dict in requester_is_following]
    return query.where(
        or_(
            SnapsModel.privacy == 1,
            SnapsModel.user_id.in_(followed_by_user_list),
        ),
    )
