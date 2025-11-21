import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import storage
from app.database import get_db
from app.schemas import Project, ProjectCreate, ProjectCreateRequest, ProjectAnalysis


router = APIRouter()


ANALYZER_URL = os.getenv("ANALYZER_URL", "http://localhost:8002/analyze")


async def fetch_analysis(repo_url: str, token: str) -> ProjectAnalysis:
    """
    Вызов внешнего сервиса-анализатора.
    Ожидается, что он вернёт JSON в формате ProjectAnalysis.
    """
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(ANALYZER_URL, json={"repo_url": repo_url, "token": token})
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ошибка при обращении к сервису анализа репозитория: {exc}",
        ) from exc

    data = response.json()
    try:
        return ProjectAnalysis.model_validate(data)
    except Exception as exc:  # валидация структуры
        raise HTTPException(
            status_code=502,
            detail=f"Сервис анализа вернул неожиданный формат данных: {exc}",
        ) from exc


@router.post("", response_model=Project, status_code=201)
async def add_project(payload: ProjectCreateRequest, db: Session = Depends(get_db)) -> Project:
    """
    Добавить проект.

    Обязательные поля:
    - name — название проекта
    - url — ссылка на репозиторий
    - clone_token — токен для клонирования
    - user_id — id пользователя-владельца
    Анализ репозитория (стек, entrypoints и т.д.) вычисляется автоматически через
    внешний сервис ANALYZER_URL и сохраняется вместе с проектом.
    """
    analysis = await fetch_analysis(str(payload.url), str(payload.clone_token))
    project_create = ProjectCreate(**payload.model_dump(), analysis=analysis)
    return storage.create_project(db, project_create)


@router.get("", response_model=list[Project])
async def get_projects(db: Session = Depends(get_db)) -> list[Project]:
    """Получить список всех проектов."""
    return storage.list_projects(db)



