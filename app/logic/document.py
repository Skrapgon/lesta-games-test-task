from collections import Counter
import time
from typing import Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from logic.huffman import encode, get_huffman_code
from infra.models import Document, DocumentStatistic
from logic.text_utils import get_text_length, split_text

async def create_doc(db: AsyncSession, user_id: str, doc_name: str, text_str: str) -> Document:
    start_time = time.monotonic()
    
    words_count = get_text_length(text_str)
    huffman = encode(text_str, get_huffman_code(text_str))
    
    doc = Document(name=doc_name, text=text_str, length=words_count, author_id=user_id, huffman=huffman)
    
    db.add(doc)
    await db.flush()
    
    words_list = split_text(text_str)
    word_counts = Counter(words_list)
    
    statistics = []
    for word, count in word_counts.items():
        tf = count / words_count
        stat = DocumentStatistic(
            doc_id=doc.id,
            word=word,
            count=count,
            tf=tf,
        )
        statistics.append(stat)

    db.add_all(statistics)
    
    end_time = time.monotonic()
    doc.process_time = round(end_time - start_time, 3)
    
    await db.commit()
    return doc
    
async def get_doc_by_id(db: AsyncSession, doc_id: str) -> Document:
    doc = await db.execute(
        select(Document)
        .where(Document.id == doc_id)
        .options(
            selectinload(Document.collections),
            selectinload(Document.statistics)
            )
        )
    return doc.scalar_one_or_none()
    
async def get_docs_by_user(db: AsyncSession, user_id: str) -> Sequence[Document]:
    docs = await db.execute(select(Document).where(Document.author_id == user_id))
    return docs.scalars().all()

async def get_docs_by_collection(db: AsyncSession, collection_id: str) -> Sequence[Document]:
    docs = await db.execute(
        select(Document)
        .join(Document.collections)
        .where(Document.collections.any(id == collection_id))
    )
    return docs.scalars().all()

async def delete_doc(db: AsyncSession, doc_id: str) -> Document:
    doc = await get_doc_by_id(db, doc_id)
    if doc:
        await db.delete(doc)
        await db.commit()
    return doc
    
async def get_doc_stat(db: AsyncSession, doc_id: str, offset: int = 0, limit: int = 50) -> Sequence[DocumentStatistic]:
    doc = await get_doc_by_id(db, doc_id)
    if not doc:
        return
    stats = await db.execute(
        select(DocumentStatistic)
        .where(DocumentStatistic.doc_id == doc_id)
        .order_by(desc(DocumentStatistic.tf))
        .offset(offset)
        .limit(limit)
    )
    return stats.scalars().all()