from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from typing import List
from sqlalchemy import func, select, delete, insert, update
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime, timedelta

from models import History, Weather
from database import get_async_session
import tables


class HistoryService:
    def __init__(self, session: Session = Depends(get_async_session)):
        self.session = session

    async def _check_day_in_history(self, cur_date: date):
        """
        Проверка наличия записи в таблицу History о средней температуре за проверяемую дату
        :param cur_date: проверяемая дата
        :return: True - если запись есть, False - если записи нет
        """
        res = await (
            self.session
            .execute(
                select(tables.History)
                .filter(tables.History.date == cur_date)
            )
        )
        return res

    async def _getting_data_from_day_table(self):
        """
        Получение данных из таблицы Day
        :return: Список посчитанных средних температур с их датами (на основе данных из таблицы Day)
        """
        days_weather = await (
            self.session
            .execute(
                select(
                    tables.DayWeather.date,
                    func.avg(tables.DayWeather.temp)
                )
                .group_by(tables.DayWeather.date)
            )
        )
        return days_weather.all()

    async def _delete_old_records_in_table_day(self):
        """
        Удаление старых записей, по которым уже посчитана средняя температура
        и не требуется хранение почасовой температуры
        """
        now = datetime.now()
        today = now.date()
        await (
            self.session
            .execute(
                delete(tables.DayWeather)
                .filter(
                    now - tables.DayWeather.datetime > timedelta(hours=1),
                    tables.DayWeather.date != today
                )
            )
        )

    async def _update_history_table(self, days_weather):
        """
        Обогащение таблицы History новыми данными
        :param days_weather: Список, полученный в результате работы фукнции self._getting_data_from_day_table()
        """
        for cur_date, cur_temp in days_weather:
            day_in_history = await self._check_day_in_history(cur_date)
            if day_in_history.scalars().first():
                await (
                    self.session
                    .execute(
                        update(tables.History)
                        .where(tables.History.date == cur_date)
                        .values(
                            {
                                "temp": cur_temp
                            }
                        )
                    )
                )
            else:
                await (
                    self.session
                    .execute(
                        insert(tables.History)
                        .values(
                            date=cur_date,
                            temp=cur_temp
                        )
                    )
                )

    async def get_history(self) -> List[History]:
        days_weather = await self._getting_data_from_day_table()

        await self._delete_old_records_in_table_day()

        await self._update_history_table(days_weather)

        all_history = await (
            self.session
            .execute(
                select(tables.History)
            )
        )

        try:
            await self.session.commit()
            return all_history.scalars().all()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=422)

