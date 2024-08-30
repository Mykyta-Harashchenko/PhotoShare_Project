import os
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..entity import models
from ..schemas import photos as schemas
from unidecode import unidecode

cloudinary.config(
    cloud_name='dkys',
    api_key='36348',
    api_secret='n8kGXFoc7BU1cXSi'
)

def upload_image(file_path: str, folder: str = None, overwrite: bool = True) -> dict:
    """
    Завантажує зображення на Cloudinary.

    :param file_path: Шлях до файлу зображення на локальному диску.
    :param folder: Папка на Cloudinary, де зберігатиметься зображення.
    :param overwrite: Визначає, чи перезаписувати існуючі файли.
    :return: Словник з інформацією про завантажений файл, включаючи URL.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Файл {file_path} не знайдено.")
    
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    public_id = unidecode(file_name).replace(' ', '_')
    
    response = cloudinary.uploader.upload(file_path, public_id=public_id, folder=folder, overwrite=overwrite)
    return response

async def create_photo(db: AsyncSession, photo: schemas.PhotoCreate, user_id: int) -> models.Post:
    """
    Створює нову світлину, завантажує її на Cloudinary і зберігає URL у базі даних.

    :param db: Асинхронна сесія бази даних.
    :param photo: Схема PhotoCreate з даними про світлину.
    :param user_id: Ідентифікатор користувача, який завантажує світлину.
    :return: Створена світлина (Post).
    """
    result = upload_image(photo.url)  
    if not result:
        raise ValueError("Не вдалося завантажити зображення на Cloudinary.")

    image_url = result.get('secure_url')

    db_post = models.Post(
        foto=image_url,
        description=photo.description,
        owner_id=user_id
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

async def get_photo(db: AsyncSession, photo_id: int) -> models.Post:
    """
    Отримує світлину за її унікальним ідентифікатором.

    :param db: Асинхронна сесія бази даних.
    :param photo_id: Унікальний ідентифікатор світлини (Post).
    :return: Світлина (Post) або None, якщо світлину не знайдено.
    """
    result = await db.execute(select(models.Post).filter(models.Post.id == photo_id))
    return result.scalar_one_or_none()

async def get_photos_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10) -> list[models.Post]:
    """
    Отримує всі світлини, завантажені користувачем.

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

async def update_photo(db: AsyncSession, photo_id: int, updated_photo: schemas.PhotoUpdate) -> models.Post:
    """
    Оновлює опис світлини та, за необхідності, її зображення.

    :param db: Асинхронна сесія бази даних.
    :param photo_id: Унікальний ідентифікатор світлини (Post).
    :param updated_photo: Схема PhotoUpdate з новими даними для світлини.
    :return: Оновлена світлина (Post) або None, якщо світлину не знайдено.
    """
    result = await db.execute(select(models.Post).filter(models.Post.id == photo_id))
    db_post = result.scalar_one_or_none()
    
    if db_post:
        db_post.description = updated_photo.description

        if updated_photo.url:
            upload_result = upload_image(updated_photo.url)
            db_post.foto = upload_result.get('secure_url')

        await db.commit()
        await db.refresh(db_post)
    return db_post

async def delete_photo(db: AsyncSession, photo_id: int) -> models.Post:
    """
    Видаляє світлину з бази даних та Cloudinary.

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
