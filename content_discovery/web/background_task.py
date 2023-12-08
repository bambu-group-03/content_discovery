import asyncio
import datetime
from typing import Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO
from content_discovery.notifications import Notifications

PERIOD_SECONDS = 5


class BackgroundTask:
    """Background process that continuously pings and handles trending topics"""

    def __init__(self) -> None:
        self.app = None
        self.session: AsyncSession
        self.running = True
        self.cutoff = datetime.timedelta(weeks=1)
        self.deleting_delta = datetime.timedelta(hours=3)
        self.period_deleting_minutes = 5

    async def monitor_new_trending_topics(self, an_app: Any) -> None:
        """Handle trending topics background process"""
        self.app = an_app
        self.session = an_app.state.db_session_factory()

        # snap_dao = SnapDAO(self.session)
        trend_dao = TrendingTopicDAO(self.session)
        hashtag_dao = HashtagDAO(self.session)

        while self.running:
            date = datetime.datetime.now() - self.cutoff
            tags = await hashtag_dao.get_top_hashtags(
                cutoff_date=date,
                minimum_hashtag_count=4,
            )
            if tags:
                # store all tags in trend database
                new_tags = await self._store(tags, trend_dao)
                # send notif
                if new_tags:
                    await self._send_notification(new_tags)

            await asyncio.sleep(PERIOD_SECONDS)

        print("return from task")

    async def delete_old_trending_topic(self, an_app: Any) -> None:
        """Handle trending topics background process"""
        self.app = an_app
        self.session = an_app.state.db_session_factory()

        trend_dao = TrendingTopicDAO(self.session)

        while self.running:
            await trend_dao.delete_old_trending_topics(self.deleting_delta)
            await asyncio.sleep(60 * self.period_deleting_minutes)

    def kick_off_background_tasks(self, an_app: Any) -> None:
        """Kick off background tasks."""
        print("Tasks Started")
        asyncio.create_task(background_task.monitor_new_trending_topics(an_app))
        asyncio.create_task(background_task.delete_old_trending_topic(an_app))
        print("Tasks Created")

    async def _send_notification(self, new_tags: List[Any]) -> None:
        first_tag = max(new_tags, key=lambda tag: tag["count"])
        await Notifications().send_trending_notification(first_tag["name"])

    async def _store(self, tags: List[Any], trend_dao: TrendingTopicDAO) -> List[Any]:
        new_tags = []
        for tag in tags:
            new_tag = await trend_dao.create_topic_model(name=tag["name"])
            if new_tag:
                new_tags.append(tag)
        return new_tags


background_task = BackgroundTask()
