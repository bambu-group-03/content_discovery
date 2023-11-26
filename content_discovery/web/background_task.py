import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO
from content_discovery.web.api.utils import send_notification


class BackgroundTask:
    """Background process that continuously pings and handles trending topics"""

    def __init__(self) -> None:
        self.text = ""
        self.VAR = 0
        self.app = None
        self.session: AsyncSession
        self.running = True
        self.MAX_SNAPS = 10000

    async def my_task(self, an_app: Any) -> None:
        """Handle trending topics background process"""
        print("task")
        self.app = an_app
        self.session = an_app.state.db_session_factory()

        snap_dao = SnapDAO(self.session)
        trend_dao = TrendingTopicDAO(self.session)

        while self.running:
            snaps = await snap_dao.get_all_snaps(self.MAX_SNAPS, 0)
            self.text = str(snaps)
            if snaps:
                # topic = TrendingTopicModel(name=snaps[0].content)
                # self.session.add(topic)
                # await self.session.flush()
                # await self.session.commit()
                # await self.session.close()
                await trend_dao.create_topic_model(name=snaps[0].content)
                send_notification("Hey!", "This is a notification!")
                await asyncio.sleep(10)

        print("return from task")


bgtask = BackgroundTask()


def do_startup(an_app: Any) -> None:
    """Kick off background task (should be instance method)"""
    bgtask.VAR = 13
    print("Task Started")
    asyncio.create_task(bgtask.my_task(an_app))
    print("Task Created")
