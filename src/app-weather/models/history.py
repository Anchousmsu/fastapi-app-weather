from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class HistoryBase(BaseModel):
    date: date
    temp: Decimal

    class Config:
        orm_mode = True


class History(HistoryBase):
    pass


class HistoryWithID(HistoryBase):
    id: int

