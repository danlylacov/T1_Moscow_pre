import os
import traceback

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import storage
from app.database import get_db
from app.schemas import Project, ProjectCreate, ProjectCreateRequest, ProjectAnalysis


router = APIRouter()


ANALYZER_URL = os.getenv("ANALYZER_URL", "http://localhost:8001/analyze")


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
    
    # Нормализуем данные: конвертируем test_runner из списка в строку, если необходимо
    if "test_runner" in data and isinstance(data["test_runner"], list):
        data["test_runner"] = data["test_runner"][0] if data["test_runner"] else None
    
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
    Анализ репозитория (стек, entrypoints и т.д.) вычисляется автоматически через
    внешний сервис ANALYZER_URL и сохраняется вместе с проектом.
    """
    try:
        analysis = await fetch_analysis(str(payload.url), str(payload.clone_token))
        project_create = ProjectCreate(**payload.model_dump(), analysis=analysis)
        return storage.create_project(db, project_create)
    except HTTPException:
        # Пробрасываем HTTP исключения как есть
        raise
    except Exception as exc:
        # Логируем полную ошибку для отладки
        error_trace = traceback.format_exc()
        print(f"Error in add_project: {exc}\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера при создании проекта: {str(exc)}",
        ) from exc


@router.get("", response_model=list[Project])
async def get_projects(db: Session = Depends(get_db)) -> list[Project]:
    """Получить список всех проектов."""
    return storage.list_projects(db)



