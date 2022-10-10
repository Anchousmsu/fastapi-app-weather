from fastapi import FastAPI
import asyncio

from database import async_engine, async_session
from services import TimeCheckerService
from tables import Base
from api import router


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    while True:
        async with async_session() as session:
            await TimeCheckerService(session).time_write_to_db()
        await asyncio.sleep(60)

#
# @app.on_event("shutdown")
# async def shutdown_event():
#     await async_engine.dispose()

