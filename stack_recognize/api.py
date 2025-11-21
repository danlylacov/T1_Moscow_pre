"""FastAPI-обертка над сервисом анализа технологического стека.

На вход:
    - repo_url: ссылка на Git-репозиторий
    - token: (опционально) токен доступа, если репозиторий приватный

На выход:
    JSON в формате:
    {
      "languages": [...],
      "frameworks": [...],
      "frontend_frameworks": [...],
      "backend_frameworks": [...],
      "package_manager": "pip",
      "test_runner": "pytest",
      "docker": true,
      "kubernetes": false,
      "terraform": false,
      "databases": ["sqlite"],
      "entry_points": [
        {"path": "main.py", "type": "main", "lang": "python", "confidence": 0.7},
        {"path": "VolumeHub.V2.0/bot.py", "type": "main", "lang": "python", "confidence": 0.9}
      ],
      "main_entry": {"path": "VolumeHub.V2.0/bot.py", "type": "main", "lang": "python", "confidence": 0.9}
    }
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

try:
    # Использование как пакет
    from .detector import ProjectStackDetector
    from .models import ProjectStack, EntryPoint
except ImportError:
    # Использование как простой модуль
    from detector import ProjectStackDetector
    from models import ProjectStack, EntryPoint


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tech Stack Analyzer API",
    description="FastAPI-обертка над сервисом анализа технологического стека репозитория",
    version="1.0.0",
)


# --------- Pydantic-модели запроса/ответа ---------


class AnalyzeRequest(BaseModel):
    """Входные данные для анализа репозитория."""

    repo_url: HttpUrl = Field(..., description="URL Git-репозитория")
    token: Optional[str] = Field(
        None,
        description=(
            "Опциональный токен доступа для приватных репозиториев. "
            "Может быть персональный токен GitHub/GitLab."
        ),
    )


class EntryPointOut(BaseModel):
    """Описание точки входа в формате API."""

    path: str = Field(..., description="Путь к файлу точки входа")
    type: str = Field(..., description="Тип точки входа (app/server/main/config)")
    lang: Optional[str] = Field(None, description="Язык точки входа")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Уверенность определения 0.0-1.0")


class MainEntryOut(BaseModel):
    """Основная точка входа."""

    path: str
    type: str
    lang: Optional[str]
    confidence: float


class AnalysisResponse(BaseModel):
    """Ответ API с данными о технологическом стеке."""

    languages: List[str] = []
    frameworks: List[str] = []
    frontend_frameworks: List[str] = []
    backend_frameworks: List[str] = []
    package_manager: Optional[str] = None
    test_runner: Optional[str] = None
    docker: bool = False
    docker_context: Optional[str] = None
    dockerfile_path: Optional[str] = None
    kubernetes: bool = False
    terraform: bool = False
    databases: List[str] = []
    entry_points: List[EntryPointOut] = []
    main_entry: Optional[MainEntryOut] = None


# --------- Вспомогательные функции ---------


def _build_authenticated_url(repo_url: str, token: Optional[str]) -> str:
    """Построить URL с токеном, если он передан.

    Простой универсальный вариант:
    - https://gitlab.com/...  -> https://oauth2:<token>@gitlab.com/...
    - https://github.com/... -> https://<token>@github.com/...

    Пользователь при желании может сам передавать уже готовый URL с токеном,
    тогда он будет использован без изменений.
    """
    if not token:
        return repo_url

    # Если в URL уже есть креды, не трогаем
    if "@" in repo_url:
        return repo_url

    if "://" not in repo_url:
        # Нестандартный формат, лучше не модифицировать
        return repo_url

    scheme, rest = repo_url.split("://", 1)

    if "gitlab" in rest:
        # GitLab обычно ожидает oauth2:<token>@host
        return f"{scheme}://oauth2:{token}@{rest}"

    # Для GitHub и прочих хостов просто используем <token>@host
    return f"{scheme}://{token}@{rest}"


def _serialize_entry_point(ep: EntryPoint) -> EntryPointOut:
    """Преобразование внутренней модели EntryPoint в формат API."""
    return EntryPointOut(
        path=ep.file_path,
        type=ep.type,
        lang=ep.language,
        confidence=ep.confidence,
    )


def _serialize_main_entry(ep: Optional[EntryPoint]) -> Optional[MainEntryOut]:
    if ep is None:
        return None

    return MainEntryOut(
        path=ep.file_path,
        type=ep.type,
        lang=ep.language,
        confidence=ep.confidence,
    )


def _stack_to_response(stack: ProjectStack) -> AnalysisResponse:
    """Конвертация ProjectStack в pydantic-модель ответа."""
    entry_points_out = [_serialize_entry_point(ep) for ep in stack.entry_points]

    docker_context, dockerfile_path = _extract_docker_paths(stack)

    return AnalysisResponse(
        languages=stack.languages,
        frameworks=stack.frameworks,
        frontend_frameworks=stack.frontend_frameworks,
        backend_frameworks=stack.backend_frameworks,
        package_manager=stack.package_manager,
        test_runner=stack.test_runner,
        docker=stack.docker,
        docker_context=docker_context,
        dockerfile_path=dockerfile_path,
        kubernetes=stack.kubernetes,
        terraform=stack.terraform,
        databases=stack.databases,
        entry_points=entry_points_out,
        main_entry=_serialize_main_entry(stack.main_entry_point),
    )


# --------- Маршруты FastAPI ---------


def _extract_docker_paths(stack: ProjectStack) -> tuple[Optional[str], Optional[str]]:
    """Определить docker_context и dockerfile_path из обнаруженных файлов.

    dockerfile_path — относительный путь до Dockerfile (включая имя файла).
    docker_context — директория, в которой лежит Dockerfile.
    """
    docker_files = stack.files_detected.get("docker") if hasattr(stack, "files_detected") else None
    if not docker_files:
        return None, None

    dockerfile_rel: Optional[str] = None

    for rel in docker_files:
        name = Path(rel).name
        if name.startswith("Dockerfile") or name.endswith(".dockerfile"):
            dockerfile_rel = rel
            break

    if dockerfile_rel is None:
        return None, None

    dockerfile_path = dockerfile_rel
    context_path = str(Path(dockerfile_rel).parent)
    if context_path == ".":
        context_path = ""

    return context_path, dockerfile_path


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_repo(payload: AnalyzeRequest) -> AnalysisResponse:
    """Проанализировать репозиторий и вернуть JSON с технологическим стеком."""
    detector = ProjectStackDetector()

    repo_url = str(payload.repo_url)
    auth_url = _build_authenticated_url(repo_url, payload.token)

    try:
        stack = detector.detect_stack(auth_url)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Ошибка при анализе репозитория")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return _stack_to_response(stack)


# Для локального запуска: `uvicorn api:app --reload`
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)


