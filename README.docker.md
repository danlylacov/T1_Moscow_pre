# Docker Compose для сервисов Self-Deploy

Этот docker-compose файл запускает три основных сервиса:

1. **stack_recognize** (порт 8001) - сервис анализа технологического стека репозиториев
2. **ci_generator** (порт 8000) - сервис генерации CI/CD пайплайнов
3. **core_service** (порт 8002) - основной сервис, координирующий работу других сервисов
4. **postgres** (порт 5432) - база данных PostgreSQL для core_service

## Запуск

```bash
# Запустить все сервисы
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановить все сервисы
docker-compose down

# Пересобрать и запустить
docker-compose up -d --build
```

## Проверка работы

После запуска сервисы будут доступны по адресам:

- **stack_recognize**: http://localhost:8001/docs
- **ci_generator**: http://localhost:8000/docs
- **core_service**: http://localhost:8002/docs
- **PostgreSQL**: localhost:5432

## Переменные окружения

### core_service
- `DATABASE_URL` - URL подключения к PostgreSQL (по умолчанию: postgresql+psycopg2://postgres:postgres@postgres:5432/self_deploy)
- `ANALYZER_URL` - URL сервиса stack_recognize (по умолчанию: http://stack_recognize:8000/analyze)
- `PIPELINE_GENERATOR_URL` - URL сервиса ci_generator (по умолчанию: http://ci_generator:8000/generate)

## Volumes

- `postgres_data` - постоянное хранилище для данных PostgreSQL

## Health Checks

Все сервисы имеют health checks, которые проверяют доступность эндпоинтов:
- stack_recognize: `/docs`
- ci_generator: `/docs`
- core_service: `/health`
- postgres: `pg_isready`

## Примечания

- При первом запуске PostgreSQL создаст базу данных `self_deploy`
- Core-service автоматически создаст таблицы при старте
- Все сервисы перезапускаются автоматически при сбоях (restart: unless-stopped)

