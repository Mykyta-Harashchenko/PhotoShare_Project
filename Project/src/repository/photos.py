from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..entity import models
from ..schemas import photos as schemas 
import cloudinary.uploader

async def create_photo(db: AsyncSession, photo: schemas.PhotoCreate, user_id: int):
    """
    Функція для створення нової світлини (Post) з завантаженням на Cloudinary.

    :param db: Асинхронна сесія бази даних.
    :param photo: Схема PhotoCreate з даними про світлину.
    :param user_id: Ідентифікатор користувача, який завантажує світлину.
    :return: Створена світлина (Post).
    """
    upload_result = cloudinary.uploader.upload(photo.url)
    image_url = upload_result['secure_url']

    db_post = models.Post(
        foto=image_url,  
        description=photo.description,
        owner_id=user_id
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)        
    return db_post

async def get_photo(db: AsyncSession, photo_id: int):
    """
    Отримує світлину за її унікальним ідентифікатором.

    :param db: Асинхронна сесія бази даних.
    :param photo_id: Унікальний ідентифікатор світлини (Post).
    :return: Світлина (Post) або None, якщо світлину не знайдено.
    """
    result = await db.execute(select(models.Post).filter(models.Post.id == photo_id))
    return result.scalar_one_or_none()

async def get_photos_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    """
    Отримує всі світлини (Posts), завантажені користувачем.

    :param db: Асинхронна сесія бази даних.
    :param user_id: Ідентифікатор користувача.
    :param skip: Кількість записів для пропуску (пагінація).
    :param limit: Максимальна кількість записів для повернення (пагінація).
    :return: Список світлин (Posts) користувача.
    """
    result = await db.execute(
        select(models.Post).filter(models.Post.owner_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_photo(db: AsyncSession, photo_id: int, description: str, url: str = None):
    """
    Оновлює опис світлини (Post) та, за потреби, її зображення.

    :param db: Асинхронна сесія бази даних.
    :param photo_id: Унікальний ідентифікатор світлини (Post).
    :param description: Новий опис світлини.
    :param url: Новий URL зображення, який потрібно оновити (опціонально).
    :return: Оновлена світлина (Post).
    """
    result = await db.execute(select(models.Post).filter(models.Post.id == photo_id))
    db_post = result.scalar_one_or_none()
    if db_post:
        db_post.description = description

        if url:
            upload_result = cloudinary.uploader.upload(url)
            db_post.foto = upload_result['secure_url']

        await db.commit()
        await db.refresh(db_post)
    return db_post

async def delete_photo(db: AsyncSession, photo_id: int):
    """
    Видаляє світлину (Post) з бази даних та Cloudinary.

    :param db: Асинхронна сесія бази даних.
    :param photo_id: Унікальний ідентифікатор світлини (Post).
    :return: Видалена світлина (Post) або None, якщо світлину не знайдено.
    """
    result = await db.execute(select(models.Post).filter(models.Post.id == photo_id))
    db_post = result.scalar_one_or_none()
    if db_post:
        public_id = db_post.foto.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id)
        
        await db.delete(db_post)
        await db.commit()
    return db_post
