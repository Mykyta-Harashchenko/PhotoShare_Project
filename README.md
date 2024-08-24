# PhotoShare_Project

### h3 створення міграцій
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
  можливо вимагатиме встановлення 
  psycopg2-binary
