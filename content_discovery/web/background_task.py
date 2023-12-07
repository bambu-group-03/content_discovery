import asyncio
import datetime
from typing import Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO
from content_discovery.notifications import Notifications


class BackgroundTask:
    """Background process that continuously pings and handles trending topics"""

    def __init__(self) -> None:
        self.app = None
        self.session: AsyncSession
        self.running = True
        self.MAX_SNAPS = 10000
        self.PERIOD_SECONDS = 5
        self.cutoff = datetime.timedelta(weeks=1)

    async def my_task(self, an_app: Any) -> None:
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
            if len(tags):
                # store all tags in trend database
                new_tags = await self._store(tags, trend_dao)
                # send notif
                if new_tags:
                    try:
                        await self._send_notification(new_tags)
                    except Exception as e:
                        await trend_dao.create_topic_model(name=f"sending notif failed DEBUG error {str(e)}")
                else:
                    await trend_dao.create_topic_model(name="notif failed DEBUG empty tglist")

            await asyncio.sleep(self.PERIOD_SECONDS)

        print("return from task")

    async def _send_notification(self, new_tags: List[Any]) -> None:
        first_tag = max(new_tags, key=lambda tag: tag["count"])
        print("sending trending notif")
        await Notifications().send_trending_notification(first_tag["name"])

    async def _store(self, tags: List[Any], trend_dao: TrendingTopicDAO) -> List[Any]:
        new_tags = []
        for tag in tags:
            new_tag = await trend_dao.create_topic_model(name=tag["name"])
            if new_tag:
                new_tags.append(tag)
        return new_tags


bgtask = BackgroundTask()


def do_startup(an_app: Any) -> None:
    """Kick off background task (should be instance method)"""
    print("Task Started")
    asyncio.create_task(bgtask.my_task(an_app))
    print("Task Created")
