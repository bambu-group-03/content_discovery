import asyncio


class BackgroundTask:
    def __init__(self):
        self.text = ""
        self.VAR = 0

    async def my_task(self, an_app):
        while 1:
            self.text = str(an_app) + str(self.VAR)
            self.VAR += 1
            await asyncio.sleep(1)

        print("return from task")


bgtask = BackgroundTask()


def do_startup(an_app):
    bgtask.VAR = 13
    print("Task Started")
    asyncio.create_task(bgtask.my_task(an_app))
    print("Task Created")
