from fastapi import APIRouter

from .weather import router as weather_router


router = APIRouter()

router.include_router(weather_router)
