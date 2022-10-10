from fastapi import APIRouter, Depends

from models import Weather
from services import WeatherService


router = APIRouter(
    prefix='/weather'
)


@router.get('/', response_model=Weather)
async def get_weather(service: WeatherService = Depends()):
    result = await service.get_weather()
    return result
