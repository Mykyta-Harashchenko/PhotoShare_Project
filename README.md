# PhotoShare_Project

1. Налаштувати віртуальне середовище, poetry shell
2. Docker compose up
3. Встановити всі бібліотеки з requierements.txt
4. Налаштувати .env файл, example лежить у project/src/conf
5. провести міграцію, alembic upgrade head
6. запустити проект, або python run.py, або uvicorn Project.src.main:app --reload

  можливо вимагатиме встановлення 
  psycopg2-binary
