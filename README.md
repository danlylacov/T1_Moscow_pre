# Self-Deploy

Монолитное CLI приложение для анализа технологического стека репозиториев и генерации CI/CD пайплайнов.

## Структура проекта

- `core-service/` - Основное CLI приложение
- `stack_recognize/` - Модуль анализа технологического стека
- `ci_generator/` - Модуль генерации CI/CD пайплайнов

## Установка

```bash
cd core-service
pip install -r requirements.txt
```

## Использование

### Через shell скрипты (рекомендуется)

```bash
# Инициализация базы данных
./init-db.sh

# Добавить проект
./add-project.sh --name "My Project" --url "https://github.com/user/repo" --token "your_token"

# Список проектов
./list-projects.sh

# Анализ стека проекта (вывод в консоль)
./analyze-repo.sh --url "https://github.com/user/repo" --output stack.json

# Генерация пайплайна для проекта
./generate.sh --project-id 1 --output .gitlab-ci.yml

# Генерация пайплайна напрямую из репозитория (со стеком в файл)
./generate-from-repo.sh --url "https://github.com/user/repo" --output .gitlab-ci.yml --stack-output stack.json

# История генераций
./list-pipelines.sh
```

### Через CLI напрямую

```bash
cd core-service

# Инициализация базы данных
python cli.py init

# Добавить проект
python cli.py add-project --name "My Project" --url "https://github.com/user/repo"

# Список проектов
python cli.py list-projects

# Генерация пайплайна для проекта
python cli.py generate --project-id 1 --output .gitlab-ci.yml

# Генерация пайплайна напрямую из репозитория
python cli.py generate-from-repo --url "https://github.com/user/repo" --output .gitlab-ci.yml

# История генераций
python cli.py list-pipelines
```

## Shell скрипты

В корне проекта доступны следующие скрипты:

- `init-db.sh` - Инициализация базы данных
- `add-project.sh` - Добавить проект
- `list-projects.sh` - Список проектов
- `analyze-repo.sh` - Анализ стека проекта (вывод в консоль)
- `generate.sh` - Генерация пайплайна для проекта
- `generate-from-repo.sh` - Генерация пайплайна из репозитория (с опцией сохранения стека)
- `list-pipelines.sh` - История генераций

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных (по умолчанию: `postgresql+psycopg2://postgres:postgres@localhost:5432/self_deploy`)
