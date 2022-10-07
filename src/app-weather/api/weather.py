from fastapi import APIRouter, Depends

from models import Weather
from services import WeatherService


router = APIRouter(
    prefix='/weather'
)


@router.get('/', response_model=Weather)
def get_weather(service: WeatherService = Depends()):
    return service.get_weather()
