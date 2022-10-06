from pydantic import BaseModel
from datetime import date, time
from decimal import Decimal


class Weather(BaseModel):
    temp: Decimal

    class Config:
        orm_mode = True
