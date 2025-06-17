from pydantic import BaseModel, Field
from datetime import datetime

class Version(BaseModel):
    version: str = Field(..., example='0.1.1')
    
class Status(BaseModel):
    status: str = Field(..., example='OK')
    
class Metrics(BaseModel):
    files_processed: int
    min_time_processed: float
    max_time_processed: float
    avg_time_processed: float
    latest_file_processed_timestamp: float = Field(..., example=1487477343.548853)
    avg_words_per_file: int
    avg_files_per_user: int