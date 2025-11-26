# Спецификация выходного JSON

Документ описывает все возможные варианты значений в выходном JSON проекта анализа технологического стека.

## Структура выходного JSON

```json
{
  "languages": [],
  "frameworks": [],
  "frontend_frameworks": [],
  "backend_frameworks": [],
  "package_manager": null,
  "test_runner": [],
  "docker": false,
  "docker_context": null,
  "dockerfile_path": null,
  "docker_by_category": null,
  "kubernetes": false,
  "terraform": false,
  "databases": [],
  "entry_points": [],
  "main_entry": null,
  "test_by_category": null
}
```

---

## 1. `languages` (List[str])

Список обнаруженных языков программирования. Поддерживаются только 4 языка:

### Возможные значения:
- `"python"` - Python
- `"typescript"` - TypeScript/JavaScript (`.ts`, `.tsx`, `.js`, `.jsx`)
- `"java"` - Java/Kotlin (`.java`, `.kt`, `.kts` - Kotlin нормализуется в `java`)
- `"go"` - Go (`.go`)

**Примеры:**
```json
["python"]
["python", "typescript"]
["java"]
["go", "typescript"]
```

---

## 2. `frameworks` (List[str])

Список всех обнаруженных фреймворков.

### Возможные значения:

#### Python фреймворки:
- `"django"` - Django
- `"flask"` - Flask
- `"fastapi"` - FastAPI

#### TypeScript/JavaScript фреймворки:
- `"react"` - React
- `"vue"` - Vue.js
- `"angular"` - Angular
- `"nextjs"` - Next.js
- `"express"` - Express.js
- `"nest"` - NestJS (в коде как `nestjs`, в API как `nest`)

#### Java/Kotlin фреймворки:
- `"spring"` - Spring Framework
- `"spring-boot"` - Spring Boot (приоритет над `spring`)
- `"quarkus"` - Quarkus
- `"micronaut"` - Micronaut
- `"vertx"` - Eclipse Vert.x

#### Go фреймворки:
- `"gin"` - Gin
- `"echo"` - Echo
- `"fiber"` - Fiber
- `"beego"` - Beego

**Примеры:**
```json
["django"]
["react", "express"]
["spring-boot"]
["gin"]
["vue", "nextjs"]
```

---

## 3. `frontend_frameworks` (List[str])

Список frontend фреймворков. Автоматически извлекается из `frameworks`.

### Возможные значения:
- `"react"`
- `"vue"`
- `"angular"`
- `"nextjs"`

**Примеры:**
```json
["react"]
["vue", "nextjs"]
[]
```

---

## 4. `backend_frameworks` (List[str])

Список backend фреймворков. Автоматически извлекается из `frameworks`.

### Возможные значения:

#### Python:
- `"django"`
- `"flask"`
- `"fastapi"`

#### Java/Kotlin:
- `"spring"`
- `"spring-boot"`
- `"quarkus"`
- `"micronaut"`
- `"vertx"`

#### TypeScript/JavaScript:
- `"express"`
- `"nest"`

#### Go:
- `"gin"`
- `"echo"`
- `"fiber"`
- `"beego"`

**Примеры:**
```json
["django"]
["spring-boot", "express"]
["gin"]
[]
```

---

## 5. `package_manager` (string | null)

Менеджер пакетов проекта. Приоритет определяется по приоритету файлов.

### Возможные значения:

#### TypeScript/JavaScript:
- `"npm"` - npm (по умолчанию, если найден `package.json`)
- `"yarn"` - Yarn (если найден `yarn.lock`)
- `"pnpm"` - pnpm (если найден `pnpm-lock.yaml`)

#### Python:
- `"pip"` - pip (если найден `requirements.txt` или `setup.py`)
- `"poetry"` - Poetry (если найден `pyproject.toml` с секцией `tool.poetry`)
- `"pipenv"` - Pipenv (если найден `Pipfile`)
- `"setuptools"` - Setuptools (если найден `setup.py`)

#### Java/Kotlin:
- `"maven"` - Maven (если найден `pom.xml`)
- `"gradle"` - Gradle (если найден `build.gradle` или `build.gradle.kts`)
- `"ant"` - Apache Ant (если найден `build.xml`)

#### Go:
- `"go mod"` - Go Modules (если найден `go.mod`)
- `"dep"` - Dep (устаревший)
- `"glide"` - Glide (устаревший)

#### Другие (редко встречаются):
- `"cargo"` - Rust Cargo (если найден `Cargo.toml`)
- `"bundler"` - Ruby Bundler (если найден `Gemfile`)
- `"composer"` - PHP Composer (если найден `composer.json`)
- `"mix"` - Elixir Mix (если найден `mix.exs`)
- `"pub"` - Dart Pub (если найден `pubspec.yaml`)
- `"cocoapods"` - CocoaPods (если найден `Podfile`)
- `"carthage"` - Carthage (если найден `Cartfile`)
- `"swift package manager"` - Swift Package Manager (если найден `Package.swift`)

**Примеры:**
```json
"npm"
"poetry"
"gradle"
"go mod"
null
```

---

## 6. `test_runner` (List[str])

Список обнаруженных тестовых раннеров.

### Возможные значения:

#### Python:
- `"pytest"` - pytest
- `"unittest"` - unittest (встроенный)

#### TypeScript/JavaScript:
- `"jest"` - Jest
- `"mocha"` - Mocha
- `"jasmine"` - Jasmine
- `"karma"` - Karma
- `"cypress"` - Cypress
- `"playwright"` - Playwright
- `"vitest"` - Vitest

#### Java/Kotlin:
- `"junit"` - JUnit
- `"testng"` - TestNG

#### Go:
- `"go-testing"` - Go testing package (встроенный)

#### Другие (определяются по файлам, но могут не использоваться):
- `"phpunit"` - PHPUnit
- `"rspec"` - RSpec (Ruby)
- `"cucumber"` - Cucumber (BDD)
- `"selenium"` - Selenium

**Примеры:**
```json
["pytest"]
["jest", "cypress"]
["junit"]
["go-testing"]
[]
```

---

## 7. `docker` (boolean)

Наличие Docker в проекте.

### Возможные значения:
- `true` - обнаружен `Dockerfile` или `docker-compose.yml`
- `false` - Docker не обнаружен

**Примеры:**
```json
true
false
```

---

## 8. `docker_context` (string | null)

Путь к директории, в которой находится основной Dockerfile (без имени файла).

### Возможные значения:
- Строка с путем (например: `"backend"`, `"frontend"`, `""` для корня)
- `null` - если Docker не обнаружен

**Примеры:**
```json
""
"backend"
"frontend"
null
```

---

## 9. `dockerfile_path` (string | null)

Относительный путь к основному Dockerfile (включая имя файла).

### Возможные значения:
- Строка с путем (например: `"Dockerfile"`, `"backend/Dockerfile"`)
- `null` - если Docker не обнаружен

**Примеры:**
```json
"Dockerfile"
"backend/Dockerfile"
"Dockerfile.prod"
null
```

---

## 10. `docker_by_category` (Dict[str, List[str]] | null)

Для монорепозиториев - словарь с Dockerfile по категориям.

### Структура:
```json
{
  "frontend": ["frontend/Dockerfile"],
  "backend": ["backend/Dockerfile"],
  "root": ["Dockerfile"],
  "other": ["services/api/Dockerfile"]
}
```

### Возможные ключи:
- `"frontend"` - Dockerfile в frontend директориях
- `"backend"` - Dockerfile в backend директориях
- `"root"` - Dockerfile в корне проекта
- `"other"` - прочие Dockerfile

### Возможные значения:
- Словарь с категориями и списками путей к Dockerfile
- `null` - если не монорепозиторий или только один Dockerfile

**Примеры:**
```json
{
  "frontend": ["frontend/Dockerfile"],
  "backend": ["backend/Dockerfile"]
}
null
```

---

## 11. `kubernetes` (boolean)

Наличие Kubernetes конфигураций.

### Возможные значения:
- `true` - обнаружены файлы Kubernetes (`k8s/`, `manifests/`, `*.k8s.yaml`, `Chart.yaml` для Helm)
- `false` - Kubernetes не обнаружен

**Примеры:**
```json
true
false
```

---

## 12. `terraform` (boolean)

Наличие Terraform конфигураций.

### Возможные значения:
- `true` - обнаружены файлы Terraform (`.tf`, `.terraform.lock.hcl`, `terraform.tfstate`)
- `false` - Terraform не обнаружен

**Примеры:**
```json
true
false
```

---

## 13. `databases` (List[str])

Список обнаруженных баз данных.

### Возможные значения:
- `"postgresql"` - PostgreSQL
- `"mysql"` - MySQL
- `"mongodb"` - MongoDB
- `"redis"` - Redis
- `"sqlite"` - SQLite
- `"cassandra"` - Cassandra
- `"elasticsearch"` - Elasticsearch
- `"oracle"` - Oracle Database
- `"sqlserver"` - Microsoft SQL Server

**Примеры:**
```json
["postgresql"]
["mongodb", "redis"]
["sqlite"]
[]
```

---

## 14. `entry_points` (List[EntryPointOut])

Список всех обнаруженных точек входа в приложение.

### Структура EntryPointOut:
```json
{
  "path": "main.py",
  "type": "main",
  "lang": "python",
  "confidence": 0.9
}
```

### Поля EntryPointOut:

#### `path` (string)
- Относительный путь к файлу точки входа
- Примеры: `"main.py"`, `"src/index.ts"`, `"backend/app.py"`

#### `type` (string)
Тип точки входа. Возможные значения:
- `"main"` - главная точка входа (например, `main()` функция)
- `"app"` - точка входа приложения (Flask, FastAPI, Express)
- `"server"` - точка входа сервера
- `"config"` - конфигурационная точка входа
- `"script"` - скриптовая точка входа (npm scripts)
- `"docker"` - точка входа из Dockerfile
- `"docker-compose"` - точка входа из docker-compose.yml
- `"nextjs"` - точка входа Next.js
- `"angular"` - точка входа Angular
- `"vue"` - точка входа Vue.js
- `"flask"` - специфично для Flask
- `"fastapi"` - специфично для FastAPI
- `"java"` - точка входа Java
- `"go"` - точка входа Go
- `"node"` - точка входа Node.js
- `"poetry"` - точка входа Poetry
- `"spring"` - точка входа Spring

#### `lang` (string | null)
Язык точки входа. Возможные значения:
- `"python"`
- `"typescript"`
- `"java"`
- `"go"`
- `null` - если язык не определен

#### `confidence` (float)
Уверенность в определении точки входа (0.0 - 1.0).

**Примеры:**
```json
[
  {
    "path": "main.py",
    "type": "main",
    "lang": "python",
    "confidence": 0.9
  },
  {
    "path": "src/index.ts",
    "type": "app",
    "lang": "typescript",
    "confidence": 0.8
  }
]
[]
```

---

## 15. `main_entry` (MainEntryOut | null)

Основная точка входа в приложение. Выбирается из `entry_points` по приоритету уверенности и типа.

### Структура MainEntryOut:
```json
{
  "path": "main.py",
  "type": "main",
  "lang": "python",
  "confidence": 0.9
}
```

### Поля MainEntryOut:
- Те же, что и в `EntryPointOut`

### Возможные значения:
- Объект `MainEntryOut` - основная точка входа определена
- `null` - основная точка входа не определена

**Примеры:**
```json
{
  "path": "main.py",
  "type": "main",
  "lang": "python",
  "confidence": 0.9
}
null
```

---

## 16. `test_by_category` (Dict[str, List[str]] | null)

Для монорепозиториев - словарь с тестовыми раннерами по категориям.

### Структура:
```json
{
  "frontend": ["jest", "cypress"],
  "backend": ["pytest"]
}
```

### Возможные ключи:
- `"frontend"` - тесты в frontend частях монорепозитория
- `"backend"` - тесты в backend частях монорепозитория

### Возможные значения:
- Словарь с категориями и списками тестовых раннеров
- `null` - если не монорепозиторий или тесты не категоризированы

**Примеры:**
```json
{
  "frontend": ["jest"],
  "backend": ["pytest"]
}
null
```

---

## Дополнительные поля (не присутствуют в API ответе, но есть во внутренней модели):

### `cloud_platforms` (List[str])
Обнаруженные облачные платформы:
- `"aws"` - Amazon Web Services
- `"azure"` - Microsoft Azure
- `"gcp"` - Google Cloud Platform
- `"digitalocean"` - DigitalOcean
- `"heroku"` - Heroku

### `cicd` (List[str])
Обнаруженные CI/CD системы:
- `"github-actions"` - GitHub Actions
- `"gitlab"` - GitLab CI
- `"jenkins"` - Jenkins
- `"bitbucket"` - Bitbucket Pipelines
- `"azure-pipelines"` - Azure Pipelines
- `"circleci"` - CircleCI
- `"travis"` - Travis CI
- `"teamcity"` - TeamCity
- `"bamboo"` - Bamboo

### `build_tools` (List[str])
Инструменты сборки:
- `"webpack"` - Webpack
- `"vite"` - Vite
- `"rollup"` - Rollup
- `"parcel"` - Parcel
- `"gulp"` - Gulp
- `"grunt"` - Grunt
- `"babel"` - Babel
- `"esbuild"` - esbuild
- `"swc"` - SWC
- `"make"` - Make
- `"cmake"` - CMake
- `"gradle"` - Gradle (также как менеджер пакетов)
- `"maven"` - Maven (также как менеджер пакетов)
- `"ant"` - Apache Ant

### `hints` (List[str])
Дополнительные подсказки о проекте:
- `"Наличие конфигурации веб-сервера"`
- `"Наличие конфигурации базы данных"`
- `"Наличие документации"`
- `"Наличие линтеров"`
- `"Наличие форматеров"`
- `"Наличие мониторинга"`
- `"Наличие контейнеризации"`
- `"Наличие оркестрации"`

---

## Полный пример выходного JSON

```json
{
  "languages": ["python", "typescript"],
  "frameworks": ["django", "react", "express"],
  "frontend_frameworks": ["react"],
  "backend_frameworks": ["django", "express"],
  "package_manager": "npm",
  "test_runner": ["pytest", "jest"],
  "docker": true,
  "docker_context": "",
  "dockerfile_path": "Dockerfile",
  "docker_by_category": null,
  "kubernetes": false,
  "terraform": false,
  "databases": ["postgresql", "redis"],
  "entry_points": [
    {
      "path": "backend/main.py",
      "type": "main",
      "lang": "python",
      "confidence": 0.9
    },
    {
      "path": "frontend/src/index.ts",
      "type": "app",
      "lang": "typescript",
      "confidence": 0.8
    }
  ],
  "main_entry": {
    "path": "backend/main.py",
    "type": "main",
    "lang": "python",
    "confidence": 0.9
  },
  "test_by_category": {
    "frontend": ["jest"],
    "backend": ["pytest"]
  }
}
```

---

## Особенности и ограничения

1. **Языки**: Поддерживаются только 4 языка: Python, TypeScript, Java/Kotlin, Go. Kotlin нормализуется в Java.

2. **Фреймворки**: Spring Boot имеет приоритет над Spring. Если найден Spring Boot, Spring удаляется из списка.

3. **Менеджеры пакетов**: Приоритет определяется порядком файлов в коде. Go mod имеет высший приоритет.

4. **Точки входа**: Основная точка входа выбирается по приоритету уверенности и типа. Предпочитаются типы: `main`, `app`, `docker`, `script`.

5. **Монорепозитории**: Для монорепозиториев доступны дополнительные поля: `docker_by_category` и `test_by_category`.

6. **Фильтрация**: В API ответе языки фильтруются - остаются только разрешенные 4 языка.

