from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, File, Query, UploadFile
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as Uuid

from infra.database import get_db
from auth.auth import get_current_user
from infra.models import *
from logic.collection import delete_doc_from_collection
from schema.document import Doc, DocContent, DocStat, WordDocStat
from logic.document import create_doc, delete_doc, get_doc_by_id, get_doc_stat, get_docs_by_user
from exceptions import document_404, access_denied_403

router = APIRouter(
    prefix='/api/documents',
    tags=['documents']
)

@router.post('/', response_model=Doc)
async def create_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    if not file:
        raise HTTPException(status_code=400, detail='File not provided')
    
    text_bytes = await file.read()
    if not text_bytes:
        raise HTTPException(status_code=400, detail='File is empty')

    text = text_bytes.decode('utf-8')
    
    doc = await create_doc(db, user.id, file.filename, text)
    return Doc(
        id=doc.id,
        doc_name=doc.name
    )

@router.get('/', response_model=list[Doc])
async def get_documents(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    docs = await get_docs_by_user(db, user.id)
    return [
        Doc(
            id=doc.id,
            doc_name=doc.name
        )
        for doc in docs
    ]

@router.get('/{doc_id}', response_model=DocContent)
async def get_document(
    doc_id: Annotated[Uuid, Path(..., description='Document ID')],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    doc = await get_doc_by_id(db, doc_id)
    if not doc:
        raise document_404
    if doc.author_id != user.id:
        raise access_denied_403
    
    return DocContent(id=doc_id, doc_name=doc.name, content=doc.text)
    
@router.delete('/{doc_id}')
async def delete_document(
    doc_id: Annotated[Uuid, Path(..., description='Document ID')],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    doc = await get_doc_by_id(db, doc_id)
    if not doc:
        raise document_404
    if doc.author_id != user.id:
        raise access_denied_403
    
    for collection in doc.collections:
        await delete_doc_from_collection(db, collection.id, doc.id)
    await delete_doc(db, doc_id)
    return {'status': 'deleted'}
        
@router.get('/{doc_id}/statistics', response_model=DocStat)
async def get_statistic(
    doc_id: Annotated[Uuid, Path(..., description='Document ID')],
    offset: int = Query(0, ge=0, description='Offset from the beginning'),
    limit: int = Query(50, ge=1, description='Number of items to return'),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    doc = await get_doc_by_id(db, doc_id)
    if not doc:
        raise document_404
    if doc.author_id != user.id:
        raise access_denied_403
    
    stats = await get_doc_stat(db, doc_id, offset, limit)
    return DocStat(
        id=doc_id,
        stats=[
            WordDocStat(
                word=stat.word,
                tf=stat.tf
            )
            for stat in stats
        ]
    )