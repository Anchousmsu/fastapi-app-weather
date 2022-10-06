from fastapi import FastAPI

from database import engine
from tables import Base
from api import router


Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(router)


@app.get('/history')
def history():
    return {
        'date': 2
    }
