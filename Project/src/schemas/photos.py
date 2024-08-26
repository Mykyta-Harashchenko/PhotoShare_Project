from pydantic import BaseModel, HttpUrl
from typing import Optional

class PhotoBase(BaseModel):
    """
    Базова схема для світлини, яка містить лише загальні поля.
    """
    url: HttpUrl
    description: Optional[str] = None

class PhotoCreate(PhotoBase):
    """
    Схема для створення нової світлини. Вона успадковує базові поля від PhotoBase.
    """
    foto: str
    description: Optional[str] = None

class PhotoUpdate(BaseModel):
    """
    Схема для оновлення опису світлини.
    """
    description: Optional[str] = None

class Photo(PhotoBase):
    """
    Схема для представлення світлини з додатковими даними, такими як ID та власник.
    """
    id: int
    owner_id: int

    class Config:
        orm_mode = True
