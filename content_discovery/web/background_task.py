import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO
from content_discovery.db.dao.hashtag_dao import HashtagDAO
from content_discovery.web.api.utils import send_notification
import datetime

class BackgroundTask:
    """Background process that continuously pings and handles trending topics"""

    def __init__(self) -> None:
        self.text = ""
        self.VAR = 0
        self.app = None
        self.session: AsyncSession
        self.running = True
        self.MAX_SNAPS = 10000
        self.PERIOD_SECONDS = 10
        
    async def _parse_trending_topic_from_snaps(self, hashtag_dao, snap_dao, trend_dao):
        period_to_measure = datetime.timedelta(weeks=4)
        max_hashtags = 3
        snaps = await hashtag_dao.get_top_hashtags(period_to_measure, max_hashtags)
        self.text = str(snaps)
        if snaps:
            await trend_dao.create_topic_model(name=snaps[0].content)
                
                

    async def my_task(self, an_app: Any) -> None:
        """Handle trending topics background process"""
        self.app = an_app
        self.session = an_app.state.db_session_factory()

        snap_dao = SnapDAO(self.session)
        trend_dao = TrendingTopicDAO(self.session)
        hashtag_dao = HashtagDAO(self.session)

        while self.running:
            # await self._parse_trending_topic_from_snaps(hashtag_dao, snap_dao, trend_dao)
            tags = await hashtag_dao.get_top_hashtags(None, None)
            response = send_notification("Hey!", str(tags))
            print(response)
            await asyncio.sleep(self.PERIOD_SECONDS)

        print("return from task")


bgtask = BackgroundTask()


def do_startup(an_app: Any) -> None:
    """Kick off background task (should be instance method)"""
    bgtask.VAR = 13
    print("Task Started")
    asyncio.create_task(bgtask.my_task(an_app))
    print("Task Created")
