from sqlalchemy.orm import Session
from fastapi import Depends
from decimal import Decimal
import requests

from database import get_session

CONST_KELVIN = Decimal('273.15')


class WeatherService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_weather(self):
        # получить координаты, и потом по ним получать погоду
        res = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={'lat': 55.7504461, 'lon': 37.6174943, 'appid': 'e4a6812d421ee6924022cc948e599203'}
        )
        temp = (
                Decimal(res.json().get('main').get('temp'))
                - CONST_KELVIN
        ).quantize(Decimal("1.00"))
        response = {
            'temp': temp
        }
        return response