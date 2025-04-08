from collections import Counter
from math import log10
from sqlalchemy.orm import Session

from app.domain.entities.texts import *
from app.logic.text_utils import get_text_length, split_text

def recalculate_idf(db: Session):
    total_docs_count = db.query(Doc).count()
    words = db.query(Word).all()
    for word in words:
        doc_count = (
            db.query(DocWord)
            .filter(DocWord.word_id == word.id)
            .count()
        )
        word.idf = log10(total_docs_count / doc_count)
    db.commit()

def create_doc(db: Session, text_str: str) -> Doc:
    doc = Doc(text=text_str, length=get_text_length(text_str))
    words_str = split_text(text_str)
    counter = Counter(words_str)
    
    words = []
    for word_text in counter:
        word = db.query(Word).filter_by(word=word_text).first()
        if not word:
            word = Word(word=word_text)
            db.add(word)
            db.flush()
        words.append(word)

    db.add_all(words)
    db.add(doc)
    db.commit()
    
    for word in words:
        association = DocWord(doc_id=doc.id, word_id=word.id, word_tf=counter[word.word]/doc.length)
        db.add(association)
        db.flush()

    db.commit()

    recalculate_idf(db)

    return doc