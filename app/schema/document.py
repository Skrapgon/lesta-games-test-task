from uuid import UUID
from pydantic import BaseModel

class Doc(BaseModel):
    id: UUID
    doc_name: str

class DocContent(Doc):
    content: str

class WordDocStat(BaseModel):
    word: str
    tf: float

class DocStat(BaseModel):
    id: UUID
    stats: list[WordDocStat]