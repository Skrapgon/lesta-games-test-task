from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from infra.database import get_db
from core.version import version

router = APIRouter(
    prefix='/api/info',
    tags=['info'],
)

@router.get('/status')
def get_status():
    return {'status': 'OK'}

@router.get('/version')
def get_version():
    return {'version': version}

@router.get('/metrics')
def get_metrics(db: AsyncSession = Depends(get_db)):
    ...