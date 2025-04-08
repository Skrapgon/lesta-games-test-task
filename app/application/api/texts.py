from fastapi import APIRouter, HTTPException, Path, File, Query, UploadFile
from pydantic import BaseModel
from typing import List

from app.domain.entities.texts import *
from app.infra.database import SessionLocal
from app.logic.tf_idf import create_doc

router = APIRouter(
    prefix='/api/texts',
    tags=['texts'],
)

class WordResponse(BaseModel):
    word: str
    idf: float

class DocResponse(BaseModel):
    id: int
    text_str: str
    length: int
    words: List[WordResponse]
    
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
    
    with SessionLocal() as db:
        doc = create_doc(db, text)
        return DocResponse(
            id=doc.id,
            text_str=doc.text,
            length=doc.length,
            words=[WordResponse(word=w.word, idf=w.idf) for w in doc.words]
        )


@router.get('/{doc_id}', response_model=DocResponse)
def get_text(doc_id: int = Path(..., description='Text ID')):
    with SessionLocal() as db:
        doc = db.query(Doc).filter_by(id=doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail='Document is not found')
        return DocResponse(
            id=doc.id,
            text_str=doc.text,
            length=doc.length,
            words=[WordResponse(word=w.word, idf=w.idf) for w in doc.words]
        )

@router.get('/{doc_id}/words', response_model=List[WordStat])
def get_words_stat(
    doc_id: int = Path(..., description='Text ID'),
    offset: int = Query(0, ge=0, description='Offset from the beginning'),
    limit: int = Query(50, ge=1, description='Number of items to return')
    ):
    
    with SessionLocal() as db:
        doc = db.query(Doc).filter_by(id=doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail='Document is not found')
        
        subq = (
            db.query(
                Word.word,
                Word.idf,
                DocWord.word_tf,
            )
            .join(DocWord, Word.id == DocWord.word_id)
            .filter(DocWord.doc_id == doc_id)
            .order_by(Word.idf.desc())
            .subquery()
        )
        stmt = (
            db.query(subq)
            .offset(offset)
            .limit(limit)
        )

        return [
            WordStat(
                word=row.word,
                tf=row.word_tf,
                idf=row.idf,
            )
            for row in stmt.all()
        ]