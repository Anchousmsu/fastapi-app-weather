from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List
from sqlalchemy import func
from datetime import date, datetime, timedelta

from models import History, Weather
from database import get_session
import tables


class HistoryService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _check_day_in_history(self, cur_date: date):
        """
        Проверка наличия записи в таблицу History о средней температуре за проверяемую дату
        :param cur_date: проверяемая дата
        :return: True - если запись есть, False - если записи нет
        """
        return (
            self.session
            .query(tables.History)
            .filter(tables.History.date == cur_date)
            .first()
        )

    def _getting_data_from_day_table(self):
        """
        Получение данных из таблицы Day + удаление старых записей, по которым уже посчитана средняя температура
        и не требуется хранение почасовой температуры
        :return: Список посчитанных средних температур с их датами (на основе данных из таблицы Day)
        """
        now = datetime.now()
        today = now.date()
        days_weather = (
            self.session
            .query(
                tables.DayWeather.date,
                func.avg(tables.DayWeather.temp)
            )
            .group_by(tables.DayWeather.date)
            .all()
        )

        (
            self.session
            .query(tables.DayWeather)
            .filter(
                now - tables.DayWeather.datetime > timedelta(hours=1),
                tables.DayWeather.date != today
            )
            .delete(synchronize_session='fetch')
        )
        return days_weather

    def _update_history_table(self, days_weather):
        """
        Обогащение таблицы History новыми данными
        :param days_weather: Список, полученный в результате работы фукнции self._getting_data_from_day_table()
        """
        for cur_date, cur_temp in days_weather:
            if self._check_day_in_history(cur_date):
                (
                    self.session
                    .query(tables.History)
                    .filter(tables.History.date == cur_date)
                    .update(
                        {
                            "temp": cur_temp
                        }
                    )
                )
            else:
                (
                    self.session
                    .add(
                        tables.History(
                            date=cur_date,
                            temp=cur_temp
                        )
                    )
                )

    def get_history(self) -> List[History]:
        days_weather = self._getting_data_from_day_table()

        self._update_history_table(days_weather)

        all_history = (
            self.session
            .query(tables.History)
            .all()
        )

        self.session.commit()

        return all_history
