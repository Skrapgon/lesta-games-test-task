from math import log10
from typing import Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from infra.models import Collection, Document, CollectionStatistic
from logic.document import get_doc_by_id

async def create_coll(db: AsyncSession, user_id: str, coll_name: str | None = None) -> Collection:
    collection = Collection(author_id=user_id)
    
    db.add(collection)
    await db.flush()
    
    name = f'Collection {collection.id}' if not coll_name or coll_name == '' else coll_name
    collection.name = name
    
    await db.commit()
    return collection
    
async def get_coll(db: AsyncSession, collection_id: str) -> Collection:
    collection = await db.execute(
        select(Collection)
        .options(
            selectinload(Collection.documents),
            selectinload(Collection.statistics)
            )
        .where(Collection.id == collection_id)
        )
    return collection.scalar_one_or_none()
    
async def get_colls(db: AsyncSession, user_id: str) -> Sequence[Collection]:
    collections = await db.execute(select(Collection).where(Collection.author_id == user_id))
    return collections.scalars().all()
    
async def delete_coll(db: AsyncSession, collection_id: str) -> Collection:
    collections = await get_coll(db, collection_id)
    if collections:
        await db.delete(collections)
        await db.commit()   
    return collections
    
async def add_doc_to_collection(db: AsyncSession, collection_id: str, doc_id: str) -> Collection:
    collection = await get_coll(db, collection_id)
    if not collection:
        return
    doc = await get_doc_by_id(db, doc_id)
    if not doc:
        return
    if doc not in collection.documents:
        collection.documents.append(doc)
        collection.total_words += doc.length
        await update_collection_statistics(db, collection, doc)
        await db.commit()
    return collection
    
async def delete_doc_from_collection(db: AsyncSession, collection_id: str, doc_id: str) -> Collection:
    collection = await get_coll(db, collection_id)
    if not collection:
        return
    doc = await get_doc_by_id(db, doc_id)
    if not doc:
        return
    if doc in collection.documents:
        collection.documents.remove(doc)
        collection.total_words -= doc.length
        await update_collection_statistics(db, collection, doc, False)
        await db.commit()
    return collection

async def get_collection_stat(
    db: AsyncSession,
    collection_id: str,
    offset: int = 0,
    limit: int = 50
    ) -> Sequence[CollectionStatistic]:
    collection = await get_coll(db, collection_id)
    if not collection:
        return
    stats = await db.execute(
        select(CollectionStatistic)
        .where(CollectionStatistic.coll_id == collection_id)
        .order_by(desc(CollectionStatistic.tf))
        .offset(offset)
        .limit(limit)
    )
    return stats.scalars().all()
        
async def update_collection_statistics(
    db: AsyncSession,
    collection: Collection,
    doc: Document,
    operation: bool = True
    ):
    if not collection or not doc:
        return

    existing_stats = {stat.word: stat for stat in collection.statistics}
    
    doc_stats = {stat.word: stat for stat in doc.statistics}
    doc_count = len(collection.documents)

    to_delete = []

    for word, doc_stat in doc_stats.items():
        if word in existing_stats:
            stat = existing_stats[word]

            if operation:
                stat.count += doc_stat.count
                stat.word_doc_occurrences += 1
            else:
                stat.count -= doc_stat.count
                stat.word_doc_occurrences -= 1

                if stat.count <= 0 or stat.word_doc_occurrences <= 0:
                    to_delete.append(stat)
        else:
            if operation:
                new_stat = CollectionStatistic(
                    coll_id=collection.id,
                    word=word,
                    count=doc_stat.count,
                    tf=doc_stat.count / (collection.total_words or 1),
                    word_doc_occurrences=1,
                    idf=log10(doc_count)
                )
                db.add(new_stat)
                
    for word, stat in existing_stats.items():
        stat.tf = stat.count / collection.total_words if collection.total_words > 0 else 0.0
        stat.idf = log10(doc_count / stat.word_doc_occurrences) if stat.word_doc_occurrences > 0 else 0.0 

    for stat in to_delete:
        await db.delete(stat)

    await db.commit()