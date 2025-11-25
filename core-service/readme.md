
## Health Check

### Проверка работоспособности сервиса

**GET** `/health`

Проверка работоспособности сервиса.

**Response:**
```json
{
  "status": "ok"
}
```

**Поля:**
- `status` (string, обязательное) — статус сервиса, всегда `"ok"`

---

## Users (Пользователи)

### Создание пользователя

**POST** `/users`

Создает нового пользователя в системе.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Поля запроса:**
- `username` (string, обязательное) — логин пользователя
- `password` (string, обязательное, минимум 4 символа) — пароль

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "string"
}
```

**Поля ответа:**
- `id` (integer, обязательное) — уникальный идентификатор пользователя
- `username` (string, обязательное) — логин пользователя

**Пример запроса:**
```bash
curl -X POST "http://localhost:8002/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password"
  }'
```

---

### Получение списка пользователей

**GET** `/users`

Возвращает список всех пользователей в системе.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "user1"
  },
  {
    "id": 2,
    "username": "user2"
  }
]
```

**Поля ответа (массив объектов):**
- `id` (integer, обязательное) — уникальный идентификатор пользователя
- `username` (string, обязательное) — логин пользователя

**Пример запроса:**
```bash
curl -X GET "http://localhost:8002/users"
```

---

## Projects (Проекты)

### Создание проекта

**POST** `/projects`

Создает новый проект и автоматически анализирует репозиторий через внешний сервис `stack_recognize`.

**Request Body:**
```json
{
  "name": "string",
  "url": "https://github.com/user/repo.git",
  "clone_token": "string",
  "user_id": 1
}
```

**Поля запроса:**
- `name` (string, обязательное) — название проекта в Self-Deploy
- `url` (string, обязательное, валидный HTTP URL) — URL Git-репозитория
- `clone_token` (string, обязательное) — токен для клонирования репозитория (может быть пустой строкой для публичных репозиториев)
- `user_id` (integer, обязательное) — ID владельца проекта

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "My Project",
  "url": "https://github.com/user/repo.git",
  "clone_token": "",
  "user_id": 1,
  "analysis": {
    "languages": ["Python", "JavaScript"],
    "frameworks": ["Django", "React"],
    "frontend_frameworks": ["React"],
    "backend_frameworks": ["Django"],
    "package_manager": "pip",
    "test_runner": "pytest",
    "docker": true,
    "docker_context": ".",
    "dockerfile_path": "Dockerfile",
    "kubernetes": false,
    "terraform": false,
    "databases": ["PostgreSQL"],
    "entry_points": [
      {
        "path": "main.py",
        "type": "script",
        "lang": "python",
        "confidence": 0.95
      }
    ],
    "main_entry": {
      "path": "main.py",
      "type": "script",
      "lang": "python",
      "confidence": 0.95
    }
  }
}
```

**Поля ответа:**
- `id` (integer, обязательное) — уникальный идентификатор проекта
- `name` (string, обязательное) — название проекта
- `url` (string, обязательное) — URL Git-репозитория
- `clone_token` (string, обязательное) — токен для клонирования
- `user_id` (integer, обязательное) — ID владельца проекта
- `analysis` (object, опциональное) — результат анализа репозитория

**Поля объекта `analysis`:**
- `languages` (array[string], по умолчанию `[]`) — список обнаруженных языков программирования (например: `["Python", "JavaScript", "TypeScript"]`)
- `frameworks` (array[string], по умолчанию `[]`) — список обнаруженных фреймворков (например: `["Django", "React", "FastAPI"]`)
- `frontend_frameworks` (array[string], по умолчанию `[]`) — список фронтенд-фреймворков (например: `["React", "Vue", "Angular"]`)
- `backend_frameworks` (array[string], по умолчанию `[]`) — список бэкенд-фреймворков (например: `["Django", "Flask", "FastAPI"]`)
- `package_manager` (string | null, опциональное) — менеджер пакетов (`"pip"`, `"npm"`, `"yarn"`, `"poetry"`, `"composer"` и т.д.)
- `test_runner` (string | null, опциональное) — тестовый раннер (`"pytest"`, `"jest"`, `"mocha"`, `"unittest"` и т.д.)
- `docker` (boolean, по умолчанию `false`) — наличие Docker (найден Dockerfile)
- `docker_context` (string, по умолчанию `""`) — контекст для Docker build (обычно `"."`)
- `dockerfile_path` (string | null, опциональное) — путь к Dockerfile (обычно `"Dockerfile"`)
- `kubernetes` (boolean, по умолчанию `false`) — наличие Kubernetes конфигураций
- `terraform` (boolean, по умолчанию `false`) — наличие Terraform конфигураций
- `databases` (array[string], по умолчанию `[]`) — список обнаруженных баз данных (например: `["PostgreSQL", "MySQL", "MongoDB"]`)
- `entry_points` (array[object], по умолчанию `[]`) — список точек входа в приложение

**Поля объекта `entry_points` (и `main_entry`):**
- `path` (string, обязательное) — путь к файлу точки входа (например: `"main.py"`, `"src/index.js"`)
- `type` (string, обязательное) — тип точки входа (`"script"`, `"module"`, `"service"`, `"application"` и т.д.)
- `lang` (string | null, опциональное) — язык программирования (`"python"`, `"javascript"`, `"typescript"` и т.д.)
- `confidence` (float, обязательное) — уровень уверенности в определении точки входа (от 0.0 до 1.0)

**Ошибки:**
- `502 Bad Gateway` — ошибка при обращении к сервису анализа репозитория или неожиданный формат данных

**Пример запроса:**
```bash
curl -X POST "http://localhost:8002/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Awesome Project",
    "url": "https://github.com/user/repo.git",
    "clone_token": "",
    "user_id": 1
  }'
```

---

### Получение списка проектов

**GET** `/projects`

Возвращает список всех проектов в системе.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Project 1",
    "url": "https://github.com/user/repo1.git",
    "clone_token": "",
    "user_id": 1,
    "analysis": {
      "languages": ["Python"],
      "frameworks": ["Django"],
      "frontend_frameworks": [],
      "backend_frameworks": ["Django"],
      "package_manager": "pip",
      "test_runner": "pytest",
      "docker": true,
      "docker_context": ".",
      "dockerfile_path": "Dockerfile",
      "kubernetes": false,
      "terraform": false,
      "databases": ["PostgreSQL"],
      "entry_points": [
        {
          "path": "manage.py",
          "type": "script",
          "lang": "python",
          "confidence": 0.98
        }
      ],
      "main_entry": {
        "path": "manage.py",
        "type": "script",
        "lang": "python",
        "confidence": 0.98
      }
    }
  },
  {
    "id": 2,
    "name": "Project 2",
    "url": "https://github.com/user/repo2.git",
    "clone_token": "",
    "user_id": 1,
    "analysis": null
  }
]
```

**Поля ответа:** аналогичны полям ответа создания проекта (массив объектов)

**Пример запроса:**
```bash
curl -X GET "http://localhost:8002/projects"
```

---

## Pipelines (Генерация пайплайнов)

### Создание генерации пайплайна

**POST** `/pipelines`

Генерирует CI/CD пайплайн на основе анализа проекта и пользовательских настроек. Использует внешний сервис `ci_generator` для генерации пайплайна.

**Request Body:**
```json
{
  "user_id": 1,
  "project_id": 1,
  "user_settings": {
    "platform": "gitlab",
    "triggers": {
      "on_push": ["main", "develop"],
      "on_merge_request": true,
      "on_tags": "v*",
      "schedule": "0 2 * * *",
      "manual": false
    },
    "stages": ["build", "test", "deploy"],
    "docker_registry": "registry.example.com",
    "docker_image": "myapp",
    "variables": {
      "NODE_ENV": "production",
      "API_KEY": "secret"
    },
    "project_name": "my-awesome-project",
    "python_version": "3.11",
    "docker_tag": "latest"
  }
}
```

**Поля запроса:**
- `user_id` (integer, обязательное) — ID пользователя, инициировавшего генерацию
- `project_id` (integer, обязательное) — ID проекта, из которого берется `analysis`
- `user_settings` (object, обязательное) — пользовательские настройки генерации

**Поля объекта `user_settings`:**
- `platform` (string, обязательное) — платформа CI/CD (`"gitlab"`, `"github"`, `"jenkins"`, `"azure"` и т.д.)
- `triggers` (object, обязательное) — настройки триггеров запуска пайплайна

**Поля объекта `triggers`:**
- `on_push` (array[string], по умолчанию `[]`) — список веток, при push в которые запускается пайплайн (например: `["main", "develop", "master"]`)
- `on_merge_request` (boolean, по умолчанию `false`) — запускать ли пайплайн на merge request / pull request
- `on_tags` (string | null, по умолчанию `""`) — паттерн тегов для запуска (например: `"v*"` для всех тегов, начинающихся с `v`)
- `schedule` (string | null, по умолчанию `""`) — расписание запуска в cron-формате (например: `"0 2 * * *"` для ежедневного запуска в 2:00)
- `manual` (boolean, по умолчанию `false`) — возможность ручного запуска пайплайна

**Остальные поля `user_settings`:**
- `stages` (array[string], по умолчанию `[]`) — список стадий пайплайна (`["build"`, `"test"`, `"deploy"`, `"lint"`, `"security"`, `"release"` и т.д.])
- `docker_registry` (string | null, по умолчанию `""`) — адрес Docker registry (например: `"registry.gitlab.com"` или `"docker.io"`)
- `docker_image` (string | null, по умолчанию `""`) — имя Docker образа (например: `"myapp"` или `"company/project"`)
- `variables` (object, по умолчанию `{}`) — переменные окружения в формате ключ-значение (например: `{"NODE_ENV": "production", "API_URL": "https://api.example.com"}`)
- `project_name` (string | null, по умолчанию `""`) — имя проекта для пайплайна (используется в названиях стадий и переменных)
- `python_version` (string | null, по умолчанию `""`) — версия Python (например: `"3.11"`, `"3.10"`, `"3.9"`)
- `docker_tag` (string | null, по умолчанию `""`) — тег для Docker образа (например: `"latest"`, `"v1.0.0"`, `"${CI_COMMIT_SHORT_SHA}"`)

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "project_id": 1,
  "uml": "stages:\n  - build\n  - test\n  - deploy\n\nbuild:\n  stage: build\n  script:\n    - echo 'Building...'\n\ntest:\n  stage: test\n  script:\n    - echo 'Testing...'\n\ndeploy:\n  stage: deploy\n  script:\n    - echo 'Deploying...'",
  "generated_at": "2024-11-24T19:55:00"
}
```

**Поля ответа:**
- `id` (integer, обязательное) — уникальный идентификатор генерации пайплайна
- `user_id` (integer, обязательное) — ID пользователя, инициировавшего генерацию
- `project_id` (integer | null, опциональное) — ID проекта, на основе которого был сгенерирован пайплайн
- `uml` (string, обязательное) — готовый пайплайн в текстовом формате (обычно YAML для GitLab CI, GitHub Actions и т.д.)
- `generated_at` (string, обязательное, ISO 8601) — дата и время генерации в формате `"YYYY-MM-DDTHH:MM:SS"`

**Ошибки:**
- `404 Not Found` — проект с указанным `project_id` не найден
- `400 Bad Request` — для проекта отсутствует `analysis` (нужно сначала проанализировать репозиторий)
- `502 Bad Gateway` — ошибка при обращении к сервису генерации пайплайна или пустой ответ

**Пример запроса:**
```bash
curl -X POST "http://localhost:8002/pipelines" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "project_id": 1,
    "user_settings": {
      "platform": "gitlab",
      "triggers": {
        "on_push": ["main"],
        "on_merge_request": true,
        "on_tags": "",
        "schedule": "",
        "manual": false
      },
      "stages": ["build", "test", "deploy"],
      "docker_registry": "",
      "docker_image": "",
      "variables": {},
      "project_name": "",
      "python_version": "3.11",
      "docker_tag": "latest"
    }
  }'
```

---

### Получение списка генераций пайплайнов

**GET** `/pipelines`

Возвращает список всех генераций пайплайнов в системе.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "project_id": 1,
    "uml": "stages:\n  - build\n...",
    "generated_at": "2024-11-24T19:55:00"
  },
  {
    "id": 2,
    "user_id": 1,
    "project_id": 2,
    "uml": "stages:\n  - test\n...",
    "generated_at": "2024-11-24T20:10:00"
  }
]
```

**Поля ответа:** аналогичны полям ответа создания пайплайна (массив объектов)

**Пример запроса:**
```bash
curl -X GET "http://localhost:8002/pipelines"
```

---

## Дополнительная информация

### Внутренние вызовы сервисов

#### 1. Анализ репозитория (при создании проекта)

При создании проекта (`POST /projects`) сервис автоматически вызывает внешний сервис `stack_recognize`:

- **URL:** определяется переменной окружения `ANALYZER_URL` (по умолчанию `http://localhost:8001/analyze`)
- **Метод:** `POST`
- **Request Body:**
  ```json
  {
    "repo_url": "https://github.com/user/repo.git",
    "token": "clone_token_value"
  }
  ```
- **Response:** ожидается JSON в формате `ProjectAnalysis`

#### 2. Генерация пайплайна (при создании пайплайна)

При создании пайплайна (`POST /pipelines`) сервис вызывает внешний сервис `ci_generator`:

- **URL:** определяется переменной окружения `PIPELINE_GENERATOR_URL` (по умолчанию `http://127.0.0.1:8000/generate`)
- **Метод:** `POST`
- **Request Body:**
  ```json
  {
    "analysis": {
      "languages": ["Python"],
      "frameworks": ["Django"],
      ...
    },
    "user_settings": {
      "platform": "gitlab",
      "triggers": {...},
      ...
    }
  }
  ```
- **Response:** ожидается текст пайплайна в теле ответа (обычно YAML)

### Формат даты и времени

Все поля типа `datetime` возвращаются в формате ISO 8601: `"YYYY-MM-DDTHH:MM:SS"`

**Примеры:**
- `"2024-11-24T19:55:00"`
- `"2024-11-24T20:10:30"`

### Обработка ошибок

Все ошибки возвращаются в формате:
```json
{
  "detail": "Описание ошибки"
}
```

**Статус-коды:**
- `200 OK` — успешный запрос
- `201 Created` — ресурс успешно создан
- `400 Bad Request` — некорректный запрос (неверные данные)
- `404 Not Found` — ресурс не найден
- `502 Bad Gateway` — ошибка при обращении к внешнему сервису

### Переменные окружения

Сервис использует следующие переменные окружения:

- `DATABASE_URL` — URL подключения к базе данных (по умолчанию PostgreSQL)
- `ANALYZER_URL` — URL сервиса анализа репозиториев (по умолчанию `http://localhost:8001/analyze`)
- `PIPELINE_GENERATOR_URL` — URL сервиса генерации пайплайнов (по умолчанию `http://127.0.0.1:8000/generate`)

### Swagger UI

Интерактивная документация API доступна по адресу: