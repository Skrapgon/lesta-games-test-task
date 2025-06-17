from pydantic import BaseModel

class Huffman(BaseModel):
    encoded_content: str | None