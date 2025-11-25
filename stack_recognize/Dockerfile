FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Устанавливаем системные зависимости (git нужен для клонирования репозиториев)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости для FastAPI-сервиса
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic

# Копируем исходники проекта в пакет stack_recognize
RUN mkdir -p /app/stack_recognize
COPY . /app/stack_recognize

EXPOSE 8000

# Запуск FastAPI-обертки как пакета stack_recognize
# Порт внутри контейнера 8000, но будет проброшен как 8001 на хост
CMD ["uvicorn", "stack_recognize.api:app", "--host", "0.0.0.0", "--port", "8000"]


