from pydantic import BaseModel


class CommentCreate(BaseModel):
    text: str


class CommentUpdate(BaseModel):
    text: str


class CommentResponse(BaseModel):
    id: int
    text: str
    created_at: str
    updated_at: str
    user_id: int
    post_id: int

    class Config:
        from_attributes = True
