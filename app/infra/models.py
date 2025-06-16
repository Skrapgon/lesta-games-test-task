import datetime

from sqlalchemy import DateTime, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4

from infra.base import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC))

    documents: Mapped[list['Document']] = relationship('Document', back_populates='author', cascade='all, delete-orphan')
    collections: Mapped[list['Collection']] = relationship('Collection', back_populates='author', cascade='all, delete-orphan')


class Document(Base):
    __tablename__ = 'docs'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(Text)
    length: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC))
    process_time: Mapped[float] = mapped_column(Float, nullable=True)

    author_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    author: Mapped['User'] = relationship('User', back_populates='documents')

    collections: Mapped[list['Collection']] = relationship(
        'Collection',
        secondary='collection_document',
        back_populates='documents'
    )

    statistics: Mapped[list['DocumentStatistic']] = relationship(
        'DocumentStatistic',
        back_populates='document',
        cascade='all, delete-orphan'
    )


class Collection(Base):
    __tablename__ = 'collections'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=True)
    total_words: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    author_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    author: Mapped['User'] = relationship('User', back_populates='collections')

    documents: Mapped[list['Document']] = relationship(
        'Document',
        secondary='collection_document',
        back_populates='collections'
    )

    statistics: Mapped[list['CollectionStatistic']] = relationship(
        'CollectionStatistic',
        back_populates='collection',
        cascade='all, delete-orphan'
    )


class CollectionDocument(Base):
    __tablename__ = 'collection_document'
    
    doc_id: Mapped[UUID] = mapped_column(ForeignKey('docs.id'), primary_key=True)
    coll_id: Mapped[UUID] = mapped_column(ForeignKey('collections.id'), primary_key=True)


class DocumentStatistic(Base):
    __tablename__ = 'document_statistics'

    doc_id: Mapped[UUID] = mapped_column(ForeignKey('docs.id'), primary_key=True)
    word: Mapped[str] = mapped_column(String, primary_key=True)

    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tf: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    document: Mapped['Document'] = relationship('Document', back_populates='statistics')
    

class CollectionStatistic(Base):
    __tablename__ = 'collection_statistics'
    
    coll_id: Mapped[UUID] = mapped_column(ForeignKey('collections.id'), primary_key=True)
    word: Mapped[str] = mapped_column(String, primary_key=True)

    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tf: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    word_doc_occurrences: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    idf: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    collection: Mapped['Collection'] = relationship('Collection', back_populates='statistics')