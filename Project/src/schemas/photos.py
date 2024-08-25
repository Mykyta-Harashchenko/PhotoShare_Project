from pydantic import BaseModel
from typing import Optional

# Базова схема для світлини, яка містить загальні поля
class PhotoBase(BaseModel):
    url: str
    description: Optional[str] = None  # Опис світлини є необов'язковим

# Схема для створення нової світлини
class PhotoCreate(PhotoBase):
    pass  # Успадковує всі поля з PhotoBase

# Схема для оновлення опису світлини
class PhotoUpdate(BaseModel):
    description: str  # Оновлення лише поля опису

# Схема для представлення світлини у відповіді
class Photo(PhotoBase):
    id: int  # Унікальний ідентифікатор світлини
    owner_id: int  # Ідентифікатор користувача-власника світлини

    class Config:
        orm_mode = True  # Дозволяє працювати зі схемою як з ORM моделлю
