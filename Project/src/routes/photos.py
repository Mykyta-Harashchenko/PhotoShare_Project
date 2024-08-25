from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import photos as photo_schemas
from ..repository import photos as photo_crud
from ..database import db
from ..services.auth import get_current_user

# Створюємо маршрутизатор для роботи зі світлинами
router = APIRouter()

# Маршрут для створення нової світлини (POST /photos/)
# photo: схема PhotoCreate з даними про світлину
# db: сесія бази даних, отримана через Depends
# current_user: поточний авторизований користувач, отриманий через Depends
@router.post("/", response_model=photo_schemas.Photo)
def create_photo(
    photo: photo_schemas.PhotoCreate, 
    db: Session = Depends(db.get_db),
    current_user: int = Depends(get_current_user)
):
    # Викликаємо функцію для створення світлини в репозиторії
    return photo_crud.create_photo(db=db, photo=photo, user_id=current_user.id)

# Маршрут для отримання світлини за її ID (GET /photos/{photo_id})
# photo_id: унікальний ідентифікатор світлини, який передається в URL
@router.get("/{photo_id}", response_model=photo_schemas.Photo)
def read_photo(
    photo_id: int, 
    db: Session = Depends(db.get_db),
    current_user: int = Depends(get_current_user)
):
    # Отримуємо світлину з бази даних
    db_photo = photo_crud.get_photo(db=db, photo_id=photo_id)
    if db_photo is None:
        # Якщо світлину не знайдено, повертаємо помилку 404
        raise HTTPException(status_code=404, detail="Photo not found")
    return db_photo  # Повертаємо знайдену світлину

# Маршрут для оновлення опису світлини (PUT /photos/{photo_id})
# description: новий опис світлини, переданий у тілі запиту
@router.put("/{photo_id}", response_model=photo_schemas.Photo)
def update_photo(
    photo_id: int, 
    description: photo_schemas.PhotoUpdate, 
    db: Session = Depends(db.get_db),
    current_user: int = Depends(get_current_user)
):
    # Отримуємо світлину з бази даних за ID
    db_photo = photo_crud.get_photo(db=db, photo_id=photo_id)
    if db_photo is None or db_photo.owner_id != current_user.id:
        # Перевіряємо, чи існує світлина та чи належить вона поточному користувачу
        raise HTTPException(status_code=404, detail="Photo not found or not authorized")
    # Оновлюємо опис світлини
    return photo_crud.update_photo(db=db, photo_id=photo_id, description=description.description)

# Маршрут для видалення світлини (DELETE /photos/{photo_id})
@router.delete("/{photo_id}", response_model=photo_schemas.Photo)
def delete_photo(
    photo_id: int, 
    db: Session = Depends(db.get_db),
    current_user: int = Depends(get_current_user)
):
    # Отримуємо світлину з бази даних за ID
    db_photo = photo_crud.get_photo(db=db, photo_id=photo_id)
    if db_photo is None or db_photo.owner_id != current_user.id:
        # Перевіряємо, чи існує світлина та чи належить вона поточному користувачу
        raise HTTPException(status_code=404, detail="Photo not found or not authorized")
    # Видаляємо світлину
    return photo_crud.delete_photo(db=db, photo_id=photo_id)
