import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Day(Base):
    __tablename__ = 'day'

    id = sa.Column(sa.Integer, primary_key=True)
    date = sa.Column(sa.Date)
    time = sa.Column(sa.Time)
    temp = sa.Column(sa.Numeric(2, 2))
