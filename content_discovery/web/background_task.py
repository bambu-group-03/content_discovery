import asyncio
from fastapi import FastAPI
from content_discovery.db.dao.trending_topic_dao import TrendingTopicModel
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
class BackgroundTask:
    def __init__(self):
        self.text = ""
        self.VAR = 0
        self.app = None
        self.session : AsyncSession 

    async def my_task(self, an_app):
        self.app = an_app
        self.session = an_app.state.db_session_factory()
        
        # add topic to datbase (better use DAO)
        topic = TrendingTopicModel(name="Football")
        self.session.add(topic)
        await self.session.flush()
        await self.session.commit()
        await self.session.close()
        
        while 1:
            self.text = str(self.session) + str(topic) + str(self.VAR)
            self.VAR += 1
            await asyncio.sleep(1)
            
        print("return from task")

bgtask = BackgroundTask()

def do_startup(an_app):
        bgtask.VAR = 13
        print("Task Started")
        asyncio.create_task(bgtask.my_task(an_app))
        print("Task Created")