from sqlalchemy.orm import Session
from fastapi import Depends
from decimal import Decimal
from typing import List
from sqlalchemy import func
import requests

from models import History, Weather
from database import get_session
import tables


class HistoryService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_history(self) -> List[History]:
        all_day = (
            self.session
            .query(tables.History.temp)
            .all()
        )
        print(all_day)
        day_weather = (
            self.session
            .query(
                tables.DayWeather.date,
                func.avg(tables.DayWeather.temp)
            )
            .group_by(tables.DayWeather.date)
            .all()
        )
        print(day_weather)
        return [
            {
                "date": "2022-10-01",
                "temp": 12.3
            },
            {
                "date": "2022-10-02",
                "temp": 12.4
            }
        ]
