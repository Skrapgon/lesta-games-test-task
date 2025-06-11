from fastapi import APIRouter, HTTPException, Path, File, Query, UploadFile
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.texts import *
from infra.database import get_db
from logic.tf_idf import create_doc

router = APIRouter(
    prefix='/api/texts',
    tags=['texts']
)

class DocResponse(BaseModel):
    id: str
    text_str: str
    length: int
    
class WordStat(BaseModel):
    word: str
    tf: float
    idf: float

@router.post('/', response_model=DocResponse)
async def add_text(file: UploadFile = File(None)):
    text = None

    if file:
        text = await file.read()
        text = text.decode('utf-8')

    if not text:
        raise HTTPException(status_code=400, detail='Text is not provided')
    
    doc = await create_doc(text)
    return DocResponse(
        id=str(doc.id),
        text_str=doc.text,
        length=doc.length,
    )

@router.get('/', response_model=list[DocResponse])
async def get_texts(db: AsyncSession = Depends(get_db)):
    docs = await db.execute(select(Doc))
    docs = docs.scalars().all()
    return [
        DocResponse(
            id=str(row.id),
            text_str=row.text,
            length=row.length,
        )
        for row in docs
    ]

@router.get('/{doc_id}/', response_model=list[WordStat])
async def get_words_stat(
    doc_id: str = Path(..., description='Text ID'),
    offset: int = Query(0, ge=0, description='Offset from the beginning'),
    limit: int = Query(50, ge=1, description='Number of items to return'),
    db: AsyncSession = Depends(get_db)
    ):
    
    doc = await db.execute(select(Doc).where(Doc.id == doc_id))
    doc = doc.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail='Document is not found')
    
    subq = (
        select(
            Word.word,
            Word.idf,
            DocWord.word_tf,
        )
        .join(DocWord, Word.id == DocWord.word_id)
        .where(DocWord.doc_id == doc_id)
        .order_by(Word.idf.desc())
    ).subquery()

    stmt = (
        select(subq)
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)

    return [
        WordStat(
            word=row.word,
            tf=row.word_tf,
            idf=row.idf,
        )
        for row in result.all()
    ]