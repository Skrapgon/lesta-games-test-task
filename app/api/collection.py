from typing import Annotated
from fastapi import APIRouter, Path, Query
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as Uuid

from infra.database import get_db
from auth.auth import get_current_user
from infra.models import *
from logic.collection import delete_doc_from_collection
from schema.collection import Collect, CollectContent, WordStat, CollectionStat, CollectCreate
from logic.document import get_doc_by_id
from logic.collection import create_coll, get_coll, get_colls, get_collection_stat, add_doc_to_collection, delete_doc_from_collection, delete_coll
from exceptions import document_404, collection_404, access_denied_403
from schema.document import Doc

router = APIRouter(
    prefix='/api/collections',
    tags=['collections']
)

@router.post('/', response_model=Collect)
async def create_collection(
    name: CollectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    '''Создание новой коллекции с названием name для текущего пользователя'''
    
    collection = await create_coll(db, user.id, name.name)
    return Collect(
        id=collection.id,
        name=collection.name
    )

@router.get('/', response_model=list[Collect])
async def get_collections(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    '''Вывод всех коллекций текущего пользователя'''
    
    collections = await get_colls(db, user.id)
    return [
        Collect(
            id=collection.id,
            name=collection.name
        )
        for collection in collections
    ]

@router.get('/{collection_id}', response_model=CollectContent)
async def get_collection(
    collection_id: Annotated[Uuid, Path(..., description='Collection ID')],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    '''Вывод содержимого указанной коллекции текущего пользователя'''
    
    collection = await get_coll(db, collection_id)
    if not collection:
        raise collection_404
    if collection.author_id != user.id:
        raise access_denied_403
    
    return CollectContent(
        id=collection_id,
        name=collection.name,
        documents=[
            Doc(
                id=doc.id,
                doc_name=doc.name
            )
            for doc in collection.documents
            ]
        )

@router.delete('/{collection_id}')
async def delete_collection(
    collection_id: Annotated[Uuid, Path(..., description='Collection ID')],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    '''Удаление указанной коллекции текущего пользователя'''
    
    collection = await get_coll(db, collection_id)
    if not collection:
        raise collection_404
    if collection.author_id != user.id:
        raise access_denied_403
    
    await delete_coll(db, collection_id)
    return {'status': 'deleted'}

@router.post('/{collection_id}/{doc_id}', response_model=CollectContent)
async def add_document_to_collection(
    collection_id: Annotated[Uuid, Path(..., description='Collection ID')],
    doc_id: Annotated[Uuid, Path(..., description='Document ID')],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    '''Добавление указанного документа в указанную коллекцию текущего пользователя'''
    
    collection = await get_coll(db, collection_id)
    if not collection:
        raise collection_404
    if collection.author_id != user.id:
        raise access_denied_403
    
    document = await get_doc_by_id(db, doc_id)
    if not document:
        raise document_404
    if document.author_id != user.id:
        raise access_denied_403
    
    collection = await add_doc_to_collection(db, collection_id, doc_id)
    return CollectContent(
        id=collection_id,
        name=collection.name,
        documents=[
            Doc(
                id=doc.id,
                doc_name=doc.name
            )
            for doc in collection.documents
            ]
        )

@router.delete('/{collection_id}/{doc_id}', response_model=CollectContent)
async def delete_document_from_collection(
    collection_id: Annotated[Uuid, Path(..., description='Collection ID')],
    doc_id: Annotated[Uuid, Path(..., description='Document ID')],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    '''Удаление указанного документа из указанной коллекции текущего пользователя'''
    
    collection = await get_coll(db, collection_id)
    if not collection:
        raise collection_404
    if collection.author_id != user.id:
        raise access_denied_403
    
    document = await get_doc_by_id(db, doc_id)
    if not document:
        raise document_404
    if document.author_id != user.id:
        raise access_denied_403
    
    collection = await delete_doc_from_collection(db, collection_id, doc_id)
    return CollectContent(
        id=collection_id,
        name=collection.name,
        documents=[
            Doc(
                id=doc.id,
                doc_name=doc.name
            )
            for doc in collection.documents
            ]
        )
    
@router.get('/{collection_id}/statistics', response_model=CollectionStat)
async def get_statistic(
    collection_id: Annotated[Uuid, Path(..., description='Collection ID')],
    offset: int = Query(0, ge=0, description='Offset from the beginning'),
    limit: int = Query(50, ge=1, description='Number of items to return'),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    '''Вывод статистики по указанной коллекции текущего пользователя:
    первые limit слов, их частота (tf) и обратная частота (idf) с начальным смещением offset,
    упорядоченные по убыванию tf'''
    
    collection = await get_coll(db, collection_id)
    if not collection:
        raise collection_404
    if collection.author_id != user.id:
        raise access_denied_403
    
    stats = await get_collection_stat(db, collection_id, offset, limit)
    return CollectionStat(
        id=collection_id,
        stats=[
            WordStat(
                word=stat.word,
                tf=stat.tf,
                idf=stat.idf
            )
            for stat in stats
        ]
    )