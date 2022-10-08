from sqlalchemy.orm import Session
from fastapi import Depends
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func
import sqlalchemy as sa
import requests

from database import get_session
from models import Weather
import tables

CONST_KELVIN = Decimal('273.15')


class WeatherService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get_last_db_record(self) -> Optional[Weather]:
        """
        Получение последней по времени записи температуры в таблицу Day
        :return: Последняя запись из таблицы или None - если нет записей
        """
        last_record = (
            self.session
            .query(tables.DayWeather)
            .filter(
                tables.DayWeather.datetime
                == sa.select(
                    func.max(tables.DayWeather.datetime)
                ).scalar_subquery()
            )
        )
        self.session.commit()
        return last_record.first()

    def _get_openweathermap_res(self) -> Decimal:
        """
        Опрос внешней системы для получения актуальной температуры
        :return:
        """
        openweathermap_res = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                'lat': 55.7504461,
                'lon': 37.6174943,
                'appid': 'e4a6812d421ee6924022cc948e599203'
            }
        )
        return (
                Decimal(openweathermap_res.json().get('main').get('temp'))
                - CONST_KELVIN
        ).quantize(Decimal("1.00"))

    def _add_new_temp_to_db(self, temp: Decimal):
        cur_weather = tables.DayWeather(
            date=datetime.today(),
            datetime=datetime.now(),
            temp=temp
        )
        self.session.add(cur_weather)
        self.session.commit()

    def get_weather(self) -> Weather:
        now = datetime.now()
        last_record_data = self._get_last_db_record()
        if (
            last_record_data
            and now - last_record_data.datetime <= timedelta(hours=1)
        ):
            return Weather(temp=last_record_data.temp)

        temp = self._get_openweathermap_res()
        self._add_new_temp_to_db(temp)

        return Weather(temp=temp)
