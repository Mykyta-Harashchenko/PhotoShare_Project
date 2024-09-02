from pydantic import BaseModel, constr
from typing import List, Optional

from pydantic.v1 import validator


class PostCreate(BaseModel):
    url: str
    qr_url: str
    description: str
    owner_id: int
    tags: Optional[List[constr(min_length=1, max_length=50)]] = []

    @validator('tags')
    def validate_tags(cls, tags):
        if tags and len(tags) > 5:
            raise ValueError('Ooops! You can only add up to 5 tags.')
        return tags


class DescUpdate(BaseModel):
    description: str | None = None


class PostResponseSchema(BaseModel):
    id: int
    description: str
    file_url: str
    tags: list[str]

    class Config:
        from_attributes = True
