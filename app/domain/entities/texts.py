from sqlalchemy import Integer, String, Text, Float, ForeignKey, Column
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column

class Base(DeclarativeBase):
    pass

class Doc(Base):
    __tablename__ = 'docs'
    __allow_unmapped__ = True
    
    id: int = mapped_column(Integer, primary_key=True)
    text: str = mapped_column(Text)
    length: int = mapped_column(Integer, default=0)
    
    words = relationship('Word', secondary='doc_word', back_populates='docs')

class Word(Base):
    __tablename__ = 'words'
    __allow_unmapped__ = True
    
    id: int = mapped_column(Integer, primary_key=True)
    word: str = mapped_column(String, unique=True)
    idf: float = mapped_column(Float, default=0.0)

    docs = relationship('Doc', secondary='doc_word', back_populates='words')
    
class DocWord(Base):
    __tablename__ = 'doc_word'
    
    doc_id = Column(ForeignKey('docs.id'), primary_key=True)
    word_id = Column(ForeignKey('words.id'), primary_key=True)
    word_tf = Column(Float, nullable=False, default=0)