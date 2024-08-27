from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import photos as photo_schemas
from ..repository import photos as photo_crud
from ..database import db
from ..services.auth import get_current_user # цю функцію потрібно зробити

router = APIRouter()

@router.post("/", response_model=photo_schemas.Photo)
async def create_photo(
    photo: photo_schemas.PhotoCreate, 
    db: AsyncSession = Depends(db),
    current_user: int = Depends(get_current_user)
):
    """
    Створює нову світлину.

    :param photo: Схема PhotoCreate з даними про світлину.
    :param db: Асинхронна сесія бази даних.
    :param current_user: Поточний авторизований користувач.
    :return: Створена світлина.
    """
    return await photo_crud.create_photo(db=db, photo=photo, user_id=current_user.id)

@router.get("/{photo_id}", response_model=photo_schemas.Photo)
async def read_photo(
    photo_id: int, 
    db: AsyncSession = Depends(db),
    current_user: int = Depends(get_current_user)
):
    """
    Отримує світлину за її ID.

    :param photo_id: Унікальний ідентифікатор світлини.
    :param db: Асинхронна сесія бази даних.
    :param current_user: Поточний авторизований користувач.
    :return: Світлина або помилка 404, якщо світлину не знайдено.
    """
    db_photo = await photo_crud.get_photo(db=db, photo_id=photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return db_photo

@router.put("/{photo_id}", response_model=photo_schemas.Photo)
async def update_photo(
    photo_id: int, 
    description: photo_schemas.PhotoUpdate, 
    db: AsyncSession = Depends(db),
    current_user: int = Depends(get_current_user)
):
    """
    Оновлює опис світлини.

    :param photo_id: Унікальний ідентифікатор світлини.
    :param description: Новий опис світлини.
    :param db: Асинхронна сесія бази даних.
    :param current_user: Поточний авторизований користувач.
    :return: Оновлена світлина або помилка 404, якщо світлину не знайдено чи доступ заборонено.
    """
    db_photo = await photo_crud.get_photo(db=db, photo_id=photo_id)
    if db_photo is None or db_photo.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Photo not found or not authorized")
    return await photo_crud.update_photo(db=db, photo_id=photo_id, description=description.description)

@router.delete("/{photo_id}", response_model=photo_schemas.Photo)
async def delete_photo(
    photo_id: int, 
    db: AsyncSession = Depends(db),
    current_user: int = Depends(get_current_user)
):
    """
    Видаляє світлину.

    :param photo_id: Унікальний ідентифікатор світлини.
    :param db: Асинхронна сесія бази даних.
    :param current_user: Поточний авторизований користувач.
    :return: Видалена світлина або помилка 404, якщо світлину не знайдено чи доступ заборонено.
    """
    db_photo = await photo_crud.get_photo(db=db, photo_id=photo_id)
    if db_photo is None or db_photo.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Photo not found or not authorized")
    return await photo_crud.delete_photo(db=db, photo_id=photo_id)
