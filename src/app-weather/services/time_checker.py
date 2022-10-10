from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime
import aiohttp

from database import get_async_session
from models import Weather
import tables

CONST_KELVIN = Decimal('273.15')


class TimeCheckerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def time_write_to_db(self):
        try:
            temp = await self._get_openweathermap_res()
        except Exception:
            pass
        else:
            await self._add_new_temp_to_db(temp)
            await self.session.commit()

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

