import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class DayWeather(Base):
    __tablename__ = 'day'

    id = sa.Column(sa.Integer, primary_key=True)
    date = sa.Column(sa.Date)
    time = sa.Column(sa.Time)
    temp = sa.Column(sa.Numeric(4, 2))


class History(Base):
    __tablename__ = 'history'

    id = sa.Column(sa.Integer, primary_key=True)
    date = sa.Column(sa.Date)
    temp = sa.Column(sa.Numeric(4, 2))

