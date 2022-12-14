from pydantic import BaseModel
from decimal import Decimal


class WeatherBase(BaseModel):
    temp: Decimal

    class Config:
        orm_mode = True


class Weather(WeatherBase):
    pass


class WeatherWithID(WeatherBase):
    id: int

