## Входные данные для эндпоинта `/generate`

Сервис предоставляет HTTP‑эндпоинт `POST /generate`, который принимает JSON следующего вида:

### Тело запроса

- **Корневой объект**:
  - **`analysis`**: объект с результатами анализа репозитория  
  - **`user_settings`**: объект с пользовательскими настройками генерации пайплайна

### Поля `analysis`

```json
{
  "languages": ["markdown", "yaml", "dockerfile", "python"],
  "frameworks": ["fastapi"],
  "frontend_frameworks": [],
  "backend_frameworks": ["fastapi"],
  "package_manager": "pip",
  "test_runner": "pytest",
  "docker": true,
  "kubernetes": true,
  "terraform": false,
  "databases": [],
  "entry_points": [
    {
      "path": "app/main.py",
      "type": "main",
      "lang": "python",
      "confidence": 0.7
    },
    {
      "path": "context:",
      "type": "docker-compose",
      "lang": null,
      "confidence": 0.7
    }
  ],
  "main_entry": {
    "path": "app/main.py",
    "type": "main",
    "lang": "python",
    "confidence": 0.7
  }
}
```

- **`languages`**: массив строк — найденные языки в репозитории  
- **`frameworks`**: массив строк — обнаруженные фреймворки  
- **`frontend_frameworks`**: массив строк — фронтенд‑фреймворки  
- **`backend_frameworks`**: массив строк — бекенд‑фреймворки  
- **`package_manager`**: строка — менеджер пакетов (например, `"pip"`)  
- **`test_runner`**: строка — тестовый раннер (например, `"pytest"`)  
- **`docker`**: boolean — используется ли Docker  
- **`kubernetes`**: boolean — используется ли Kubernetes  
- **`terraform`**: boolean — используется ли Terraform  
- **`databases`**: массив строк — используемые БД  
- **`entry_points`**: массив объектов с точками входа:
  - `path`: строка — путь к файлу/контексту
  - `type`: строка — тип (`"main"`, `"docker-compose"` и т.п.)
  - `lang`: строка или `null` — язык
  - `confidence`: число (float) — уверенность детектора
- **`main_entry`**: объект основной точки входа:
  - `path`: строка
  - `type`: строка
  - `lang`: строка
  - `confidence`: число (float)

### Поля `user_settings`

```json
{
  "platform": "gitlab",
  "triggers": {
    "on_push": ["main", "develop"],
    "on_merge_request": true,
    "on_tags": "v*",
    "schedule": "",
    "manual": false
  },
  "stages": ["install", "lint", "test", "build", "security", "deploy"],
  "docker_registry": "${CI_REGISTRY}",
  "docker_image": "${CI_REGISTRY_IMAGE}:${CI_COMMIT_REF_SLUG}",
  "variables": {
    "PYTHON_VERSION": "3.11"
  }
}
```

- **`platform`**: строка — целевая платформа CI/CD (сейчас `"gitlab"`)  
- **`triggers`**: объект с триггерами:
  - `on_push`: массив строк — ветки для запуска по push
  - `on_merge_request`: boolean — запускать ли на MR
  - `on_tags`: строка — шаблон тегов (например, `"v*"` )
  - `schedule`: строка — идентификатор/описание расписания (опционально)
  - `manual`: boolean — ручной запуск
- **`stages`**: массив строк — требуемые стадии пайплайна  
- **`docker_registry`**: строка — Docker registry (например, `"${CI_REGISTRY}"`)  
- **`docker_image`**: строка — имя образа (например, `"${CI_REGISTRY_IMAGE}:${CI_COMMIT_REF_SLUG}"`)  
- **`variables`**: объект — дополнительные CI/CD‑переменные (например, `{"PYTHON_VERSION": "3.11"}`)

### Ответ эндпоинта

В ответ на `POST /generate` сервис возвращает:

```json
{
  "yaml": "<строка с содержимым .gitlab-ci.yml>",
  "required_variables": [
    {
      "name": "DOCKER_IMAGE",
      "description": "Имя Docker-образа для сборки/деплоя",
      "required": false,
      "default_value": "${CI_REGISTRY_IMAGE}:${CI_COMMIT_REF_SLUG}",
      "example": "registry.gitlab.com/group/project:latest",
      "job_usage": ["build_and_push_docker"]
    }
  ]
}
```

- **`yaml`**: строка — сгенерированный GitLab CI/CD пайплайн  
- **`required_variables`**: массив объектов с описаниями необходимых переменных:
  - `name`: имя переменной
  - `description`: человеко‑читаемое описание
  - `required`: обязательна ли переменная
  - `default_value`: значение по умолчанию (если есть)
  - `example`: пример значения
  - `job_usage`: список jobs, в которых используется переменная

