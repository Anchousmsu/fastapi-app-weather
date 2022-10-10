from fastapi import FastAPI

from database import async_engine
from tables import Base
from api import router


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()
app.include_router(router)

