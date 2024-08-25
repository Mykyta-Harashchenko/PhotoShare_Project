from sqlalchemy.orm import Session
from ..entity import models, schemas

# Функція для створення нової світлини
# db: сесія бази даних
# photo: схема PhotoCreate, яка містить дані для створення світлини (URL та опис)
# user_id: ідентифікатор користувача, який завантажує світлину
def create_photo(db: Session, photo: schemas.PhotoCreate, user_id: int):
    # Створюємо новий екземпляр моделі Photo
    db_photo = models.Photo(
        url=photo.url,
        description=photo.description,
        owner_id=user_id
    )
    # Додаємо нову світлину до сесії і зберігаємо зміни в базі даних
    db.add(db_photo)
    db.commit()
    # Оновлюємо екземпляр з бази даних, щоб отримати його ID та інші поля
    db.refresh(db_photo)
    return db_photo  # Повертаємо створену світлину

# Функція для отримання світлини за її унікальним ідентифікатором
# db: сесія бази даних
# photo_id: унікальний ідентифікатор світлини
def get_photo(db: Session, photo_id: int):
    # Повертаємо світлину, якщо вона існує, інакше повертаємо None
    return db.query(models.Photo).filter(models.Photo.id == photo_id).first()

# Функція для отримання всіх світлин, завантажених користувачем
# db: сесія бази даних
# user_id: унікальний ідентифікатор користувача
# skip: кількість записів, які потрібно пропустити (для пагінації)
# limit: максимальна кількість записів, яку потрібно повернути (для пагінації)
def get_photos_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    # Повертаємо список світлин користувача з бази даних
    return db.query(models.Photo).filter(models.Photo.owner_id == user_id).offset(skip).limit(limit).all()

# Функція для оновлення опису світлини
# db: сесія бази даних
# photo_id: унікальний ідентифікатор світлини
# description: новий опис світлини
def update_photo(db: Session, photo_id: int, description: str):
    # Знаходимо світлину в базі даних за її ID
    db_photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if db_photo:
        # Якщо світлина знайдена, оновлюємо її опис
        db_photo.description = description
        db.commit()
        # Оновлюємо екземпляр з бази даних
        db.refresh(db_photo)
    return db_photo  # Повертаємо оновлену світлину

# Функція для видалення світлини
# db: сесія бази даних
# photo_id: унікальний ідентифікатор світлини
def delete_photo(db: Session, photo_id: int):
    # Знаходимо світлину в базі даних за її ID
    db_photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if db_photo:
        # Якщо світлина знайдена, видаляємо її з бази даних
        db.delete(db_photo)
        db.commit()
    return db_photo  # Повертаємо видалену світлину (або None, якщо світлину не було знайдено)
