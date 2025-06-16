from uuid import UUID
from pydantic import BaseModel

from schema.document import Doc

class CollectCreate(BaseModel):
    name: str

class Collect(CollectCreate):
    id: UUID
    name: str
    
class CollectContent(Collect):
    documents: list[Doc]

class WordStat(BaseModel):
    word: str
    tf: float
    idf: float
    
class CollectionStat(BaseModel):
    id: UUID
    stats: list[WordStat]