from fastapi import APIRouter, Depends
from typing import List

from models import History
from services import HistoryService


router = APIRouter(
    prefix='/history'
)


@router.get('/', response_model=List[History])
async def get_history(service: HistoryService = Depends()):
    result = await service.get_history()
    return result
