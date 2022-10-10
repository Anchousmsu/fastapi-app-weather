from fastapi import FastAPI
import asyncio

from database import async_engine, async_session
from services import TimeCheckerService
from tables import Base
from api import router

ONE_HOUR = 60 * 60


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()
app.include_router(router)


class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def run_main(self):
        while True:
            async with async_session() as session:
                await TimeCheckerService(session).time_write_to_db()
            await asyncio.sleep(ONE_HOUR)


runner = BackgroundRunner()


@app.on_event('startup')
async def app_startup():
    asyncio.create_task(runner.run_main())

