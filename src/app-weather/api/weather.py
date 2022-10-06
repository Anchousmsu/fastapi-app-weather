from fastapi import APIRouter, Depends

from models.weather import Weather
from services.weather import WeatherService


router = APIRouter(
    prefix='/weather'
)


@router.get('/', response_model=Weather)
def get_weather(service: WeatherService = Depends()):
    return service.get_weather()
