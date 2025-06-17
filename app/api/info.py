from fastapi import APIRouter, Depends

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from schema.info import Metrics, Status, Version
from infra.database import get_db
from infra.models import User, Document
from core.version import version

router = APIRouter(
    prefix='/api/info',
    tags=['info'],
)

@router.get('/status', response_model=Status)
async def get_status():
    '''Индикация, что приложение работает корректно'''
    return Status(status='OK')

@router.get('/version', response_model=Version)
async def get_version():
    '''Текущая версия проекта'''
    return Version(version=version)

@router.get('/metrics', response_model=Metrics)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    '''Число обработанных файлов, min/max/avg время обработки,
    timestamp загрузки последнего файла, средняя число слов на файл,
    среднее число файлов на пользователя'''
    doc_metrics = await db.execute(
        select(
            func.count(Document.id),
            func.min(Document.process_time),
            func.max(Document.process_time),
            func.avg(Document.process_time),
            func.max(Document.created_at),
            func.avg(Document.length)
        )
    )
    doc_count, min_time, max_time, avg_time, last_created_time, avg_doc_length = doc_metrics.one()
    
    user_metrics = await db.execute(
        select(
            func.count(User.id)
        )
    )
    
    user_count = user_metrics.scalar_one()
    
    return Metrics(
        files_processed=doc_count,
        min_time_processed=min_time,
        max_time_processed=max_time,
        avg_time_processed=avg_time,
        latest_file_processed_timestamp=last_created_time.timestamp(),
        avg_words_per_file=int(avg_doc_length),
        avg_files_per_user=doc_count // user_count if user_count > 0 else 0
    )