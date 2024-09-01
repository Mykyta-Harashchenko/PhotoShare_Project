from pydantic import BaseModel



class PostCreate(BaseModel):
    url: str
    qr_url: str
    description: str
    owner_id: int

class DescUpdate(BaseModel):
    description: str | None = None



