from collections import Counter
from math import log10
from sqlalchemy import func, select

from domain.entities.texts import *
from logic.text_utils import get_text_length, split_text
from infra.database import get_db

async def recalculate_idf():
    async for db in get_db():
        total_docs_count = await db.execute(select(func.count()).select_from(Doc))
        total_docs_count = total_docs_count.scalar_one()
        
        words = await db.execute(select(Word))
        words = words.scalars().all()
        for word in words:
            doc_count = await db.execute(
                select(func.count()).select_from(DocWord).where(DocWord.word_id == word.id)
            )
            doc_count = doc_count.scalar_one()
            word.idf = log10(total_docs_count / doc_count)
        await db.commit()

async def create_doc(text_str: str) -> Doc:
    async for db in get_db():
        doc = Doc(text=text_str, length=get_text_length(text_str))
        words_str = split_text(text_str)
        counter = Counter(words_str)
        
        words = []
        for word_text in counter:
            word = await db.execute(select(Word).filter_by(word=word_text))
            word = word.scalars().first()
            if not word:
                word = Word(word=word_text)
                db.add(word)
                await db.flush()
            words.append(word)

        db.add(doc)
        await db.commit()
        
        for word in words:
            association = DocWord(doc_id=doc.id, word_id=word.id, word_tf=counter[word.word]/doc.length)
            db.add(association)

        await db.commit()

        await recalculate_idf()

        return doc