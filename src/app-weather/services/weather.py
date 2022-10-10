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

    async def _commit_and_return(self, cur_temp):
        try:
            await self.session.commit()
            return Weather(temp=cur_temp)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=422)

    async def get_weather(self) -> Weather:
        last_record_data = await self._get_last_db_record()
        return await self._commit_and_return(last_record_data.temp)

