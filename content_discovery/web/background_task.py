import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from content_discovery.db.dao.snaps_dao import SnapDAO
from content_discovery.db.dao.trending_topic_dao import TrendingTopicDAO


class BackgroundTask:
    def __init__(self):
        self.text = ""
        self.VAR = 0
        self.app = None
        self.session: AsyncSession

    async def my_task(self, an_app):
        print("task")
        self.app = an_app
        self.session = an_app.state.db_session_factory()

        snap_dao = SnapDAO(self.session)
        trend_dao = TrendingTopicDAO(self.session)

        while 1:
            snaps = await snap_dao.get_all_snaps(10000, 0)
            self.text = str(snaps)
            print("loop")
            if len(snaps):
                # topic = TrendingTopicModel(name=snaps[0].content)
                # self.session.add(topic)
                # await self.session.flush()
                # await self.session.commit()
                # await self.session.close()
                await trend_dao.create_topic_model(name=snaps[0].content)
                print("loopssss")
                await asyncio.sleep(10)

        print("return from task")


bgtask = BackgroundTask()


def do_startup(an_app):
    bgtask.VAR = 13
    print("Task Started")
    asyncio.create_task(bgtask.my_task(an_app))
    print("Task Created")
