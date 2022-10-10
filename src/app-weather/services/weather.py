from sqlalchemy.orm import Session
from sqlalchemy import func, select, insert
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional
import sqlalchemy as sa
import aiohttp

from database import get_async_session
from models import Weather
import tables

CONST_KELVIN = Decimal('273.15')


class WeatherService:
    def __init__(self, session: Session = Depends(get_async_session)):
        self.session = session

    async def _get_last_db_record(self) -> Optional[Weather]:
        """
        Получение последней по времени записи температуры в таблицу Day
        :return: Последняя запись из таблицы или None - если нет записей
        """
        last_record = await (
            self.session
            .execute(
                select(tables.DayWeather)
                .filter(
                    tables.DayWeather.datetime
                    == sa.select(
                        func.max(tables.DayWeather.datetime)
                    ).scalar_subquery()
                )
            )
        )
        return last_record.scalars().first()

    async def _get_openweathermap_res(self) -> Decimal:
        """
        Опрос внешней системы для получения актуальной температуры
        :return:
        """
        async with aiohttp.ClientSession() as session:
            openweathermap_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': 55.7504461,
                'lon': 37.6174943,
                'appid': 'e4a6812d421ee6924022cc948e599203'
            }
            async with session.get(openweathermap_url, params=params) as resp:
                openweathermap_res = await resp.json()

        return (
                Decimal(openweathermap_res.get('main').get('temp'))
                - CONST_KELVIN
        ).quantize(Decimal("1.00"))

    async def _add_new_temp_to_db(self, temp: Decimal):
        await (
            self.session
            .execute(
                insert(tables.DayWeather)
                .values(
                    date=datetime.today(),
                    datetime=datetime.now(),
                    temp=temp
                )
            )
        )

    async def _commit_and_return(self, cur_temp):
        try:
            await self.session.commit()
            return Weather(temp=cur_temp)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=422)

    async def get_weather(self) -> Weather:
        now = datetime.now()
        last_record_data = await self._get_last_db_record()
        if (
            last_record_data
            and now - last_record_data.datetime <= timedelta(hours=1)
        ):
            return await self._commit_and_return(last_record_data.temp)

        try:
            temp = await self._get_openweathermap_res()
        except Exception:
            return Weather(temp=last_record_data.temp)

        await self._add_new_temp_to_db(temp)

        return await self._commit_and_return(temp)

