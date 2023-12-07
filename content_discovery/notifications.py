import uuid
from typing import Any, List

import httpx

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.settings import settings
from content_discovery.web.api.utils import complete_snap
from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO
from content_discovery.db.models.snaps_model import SnapsModel

class Notifications:
    """Send notifications."""

    async def notify_if_snap_is_about_trending_topic(
        self, snap : SnapsModel, hashtags: List[str], topic_dao: TrendingTopicDAO):
        topics = await topic_dao.get_all_topics()
        topic_names = [topic.name for topic in topics]
        for tag in hashtags:
            if tag in topic_names:
                await self.send_notification_of_snap_in_trending(snap)

    async def send_mention_notification(
        self,
        from_id: str,
        to_id: str,
        snap_id: uuid.UUID,
        snap_dao: SnapDAO,
    ) -> None:
        """Send mention notification."""
        json_params = {
            "from_id": from_id,
            "to_id": to_id,
            "snap": await _format_snap(snap_id, snap_dao),
        }
        print(f"params mention: {json_params}")

        try:
            httpx.post(_url_post_mention_notification(), json=json_params)
        except Exception as exc:
            print(str(exc))

    async def send_like_notification(
        self,
        from_id: str,
        to_id: str,
        snap_id: str,
        snap_dao: SnapDAO,
    ) -> None:
        """Send like notification."""
        json_params = {
            "from_id": from_id,
            "to_id": to_id,
            "snap": await _format_snap(snap_id, snap_dao),
        }
        print(f"params like: {json_params}")

        timeout = httpx.Timeout(5.0, read=5.0)

        try:
            httpx.post(_url_post_like_notification(), json=json_params, timeout=timeout)
        except Exception as exc:
            print(str(exc))

    async def send_trending_notification(
        self,
        topic: str,
    ) -> None:
        """Send trending notification."""
        params = {
            "topic": topic,
        }
        print(f"params trending: {params}")

        timeout = httpx.Timeout(5.0, read=5.0)

        httpx.post(
            _url_post_trending_notification(),
            params=params,
            timeout=timeout,
        )

    async def send_notification_of_snap_in_trending(
        self,
        snap: SnapsModel,
        topic: str,
    ) -> None:
        """Send trending snap notification."""
        params = {
            "snap": snap.id,
            "topic": topic,
        }
        timeout = httpx.Timeout(5.0, read=5.0)

        httpx.post(
            _url_post_trending_snap_notification(),
            params=params,
            timeout=timeout,
        )


async def _format_snap(snap_id: Any, snap_dao: SnapDAO) -> Any:
    snap = await snap_dao.get_snap_from_id(snap_id)

    if not snap:
        return None

    full_snap = await complete_snap(snap, snap.user_id, snap_dao)

    return {
        "id": str(full_snap.id),
        "author": full_snap.author,
        "content": full_snap.content,
        "likes": full_snap.likes,
        "shares": full_snap.shares,
        "favs": full_snap.favs,
        "created_at": str(full_snap.created_at),
        "username": full_snap.username,
        "fullname": full_snap.fullname,
        "parent_id": str(full_snap.parent_id),
        "visibility": full_snap.visibility,
        "privacy": full_snap.privacy,
        "num_replies": full_snap.num_replies,
        "has_shared": full_snap.has_shared,
        "has_liked": full_snap.has_liked,
        "has_faved": full_snap.has_faved,
        "profile_photo_url": full_snap.profile_photo_url,
    }


def _url_post_mention_notification() -> str:
    print(f"{settings.identity_socializer_url}/api/notification/new_mention")
    return f"{settings.identity_socializer_url}/api/notification/new_mention"


def _url_post_like_notification() -> str:
    print(f"{settings.identity_socializer_url}/api/notification/new_like")
    return f"{settings.identity_socializer_url}/api/notification/new_like"


def _url_post_trending_notification() -> str:
    print(f"{settings.identity_socializer_url}/api/notification/new_trending")
    return f"{settings.identity_socializer_url}/api/notification/new_trending"


def _url_post_trending_snap_notification() -> str:
    print(f"{settings.identity_socializer_url}/api/notification/new_trending_snap")
    return f"{settings.identity_socializer_url}/api/notification/new_trending_snap"
