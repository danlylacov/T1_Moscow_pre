import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import storage
from app.database import get_db
from app.schemas import (
    PipelineGeneration,
    PipelineGenerationCreate,
    PipelineGenerationRequest,
    ProjectAnalysis,
    UserSettings,
)


router = APIRouter()


PIPELINE_GENERATOR_URL = os.getenv("PIPELINE_GENERATOR_URL", "http://127.0.0.1:8000/generate")


async def call_pipeline_generator(
    analysis: ProjectAnalysis, user_settings: UserSettings
) -> str:
    """
    Вызов внешнего сервиса генерации пайплайна.

    Отправляем:
    {
      "analysis": { ... },
      "user_settings": { ... }
    }

    Ожидаем, что сервис вернёт просто строку с пайплайном в теле ответа.
    """
    payload = {
        "analysis": analysis.model_dump(),
        "user_settings": user_settings.model_dump(),
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(PIPELINE_GENERATOR_URL, json=payload)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ошибка при обращении к сервису генерации пайплайна: {exc}",
        ) from exc

    # Генератор возвращает просто строку пайплайна в теле ответа
    uml = response.text
    if not uml:
        raise HTTPException(
            status_code=502,
            detail="Сервис генерации пайплайна вернул пустой ответ.",
        )
    return uml


@router.post("", response_model=PipelineGeneration, status_code=201)
async def create_pipeline_generation(
    payload: PipelineGenerationRequest, db: Session = Depends(get_db)
) -> PipelineGeneration:
    """
    Создать запись генерации пайплайна.

    Обязательные поля:
    - user_id — id пользователя, инициировавшего генерацию
    - project_id — проект, из которого берётся analysis
    - user_settings — пользовательские настройки генерации
    """
    project = storage.get_project(db, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if project.analysis is None:
        raise HTTPException(
            status_code=400,
            detail="Для данного проекта отсутствует analysis. Сначала нужно проанализировать репозиторий.",
        )

    uml = await call_pipeline_generator(project.analysis, payload.user_settings)

    create_dto = PipelineGenerationCreate(
        user_id=payload.user_id,
        project_id=payload.project_id,
        uml=uml,
    )
    return storage.create_pipeline_generation(db, create_dto)


@router.get("", response_model=list[PipelineGeneration])
async def get_pipeline_generations(db: Session = Depends(get_db)) -> list[PipelineGeneration]:
    """Получить все генерации пайплайнов."""
    return storage.list_pipeline_generations(db)

