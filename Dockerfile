# Вказуємо базовий образ Python
FROM python:3.10.10-slim

# Встановлюємо залежності системи, необхідні для роботи Python та Poetry
RUN apt-get update && apt-get install -y curl build-essential

# Встановлюємо Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Додаємо Poetry у PATH
ENV PATH="/root/.local/bin:$PATH"

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файли з вашого проєкту в контейнер
COPY pyproject.toml poetry.lock ./

# Встановлюємо залежності через Poetry
RUN poetry install --no-root

# Копіюємо весь проєкт у контейнер
COPY Project .

# Копіюємо .env файл в контейнер
COPY .env /app/.env

# Вказуємо команду для запуску сервісу
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
