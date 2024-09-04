FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && \
    apt-get install -y redis-server

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

#CMD ["uvicorn", "Project.src.main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD ["/usr/bin/supervisord"]
