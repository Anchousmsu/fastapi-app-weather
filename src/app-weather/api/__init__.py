from fastapi import APIRouter

from .weather import router as weather_router
from .history import router as history_router


router = APIRouter()

router.include_router(weather_router)
router.include_router(history_router)
