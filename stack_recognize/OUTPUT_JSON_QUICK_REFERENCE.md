# Краткая справка по выходному JSON

## Основные поля

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `languages` | `string[]` | Языки программирования | `["python", "typescript"]` |
| `frameworks` | `string[]` | Все фреймворки | `["django", "react"]` |
| `frontend_frameworks` | `string[]` | Frontend фреймворки | `["react", "vue"]` |
| `backend_frameworks` | `string[]` | Backend фреймворки | `["django", "express"]` |
| `package_manager` | `string \| null` | Менеджер пакетов | `"npm"` или `null` |
| `test_runner` | `string[]` | Тестовые раннеры | `["pytest", "jest"]` |
| `docker` | `boolean` | Наличие Docker | `true` или `false` |
| `docker_context` | `string \| null` | Директория Dockerfile | `"backend"` или `null` |
| `dockerfile_path` | `string \| null` | Путь к Dockerfile | `"Dockerfile"` или `null` |
| `docker_by_category` | `object \| null` | Dockerfile по категориям | `{"frontend": [...], "backend": [...]}` или `null` |
| `kubernetes` | `boolean` | Наличие Kubernetes | `true` или `false` |
| `terraform` | `boolean` | Наличие Terraform | `true` или `false` |
| `databases` | `string[]` | Базы данных | `["postgresql", "redis"]` |
| `entry_points` | `object[]` | Точки входа | `[{"path": "...", "type": "...", ...}]` |
| `main_entry` | `object \| null` | Основная точка входа | `{"path": "...", ...}` или `null` |
| `test_by_category` | `object \| null` | Тесты по категориям | `{"frontend": [...], "backend": [...]}` или `null` |

## Возможные значения

### Языки (`languages`)
- `python` - Python
- `typescript` - TypeScript/JavaScript
- `java` - Java/Kotlin
- `go` - Go

### Фреймворки (`frameworks`)

**Python:**
- `django`, `flask`, `fastapi`

**TypeScript/JavaScript:**
- `react`, `vue`, `angular`, `nextjs` (frontend)
- `express`, `nest` (backend)

**Java/Kotlin:**
- `spring`, `spring-boot`, `quarkus`, `micronaut`, `vertx`

**Go:**
- `gin`, `echo`, `fiber`, `beego`

### Менеджеры пакетов (`package_manager`)

**TypeScript/JavaScript:**
- `npm`, `yarn`, `pnpm`

**Python:**
- `pip`, `poetry`, `pipenv`, `setuptools`

**Java/Kotlin:**
- `maven`, `gradle`, `ant`

**Go:**
- `go mod`, `dep`, `glide`

**Другие:**
- `cargo`, `bundler`, `composer`, `mix`, `pub`, `cocoapods`, `carthage`, `swift package manager`

### Тестовые раннеры (`test_runner`)

**Python:**
- `pytest`, `unittest`

**TypeScript/JavaScript:**
- `jest`, `mocha`, `jasmine`, `karma`, `cypress`, `playwright`, `vitest`

**Java/Kotlin:**
- `junit`, `testng`

**Go:**
- `go-testing`

**Другие:**
- `phpunit`, `rspec`, `cucumber`, `selenium`

### Базы данных (`databases`)
- `postgresql`, `mysql`, `mongodb`, `redis`, `sqlite`, `cassandra`, `elasticsearch`, `oracle`, `sqlserver`

### Типы точек входа (`entry_points[].type`)
- `main`, `app`, `server`, `config`, `script`, `docker`, `docker-compose`, `nextjs`, `angular`, `vue`, `flask`, `fastapi`, `java`, `go`, `node`, `poetry`, `spring`

### CI/CD системы (внутреннее поле `cicd`)
- `github-actions`, `gitlab`, `jenkins`, `bitbucket`, `azure-pipelines`, `circleci`, `travis`, `teamcity`, `bamboo`

### Облачные платформы (внутреннее поле `cloud_platforms`)
- `aws`, `azure`, `gcp`, `digitalocean`, `heroku`

### Инструменты сборки (внутреннее поле `build_tools`)
- `webpack`, `vite`, `rollup`, `parcel`, `gulp`, `grunt`, `babel`, `esbuild`, `swc`, `make`, `cmake`, `gradle`, `maven`, `ant`

