import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app import storage
from app.database import get_db
from app.schemas import (
    PipelineGeneration,
    PipelineGenerationCreate,
    PipelineGenerationRequest,
    PipelineGenerateFromRepoRequest,
    ProjectAnalysis,
    UserSettings,
    TriggerSettings,
)


router = APIRouter()


PIPELINE_GENERATOR_URL = os.getenv("PIPELINE_GENERATOR_URL", "http://127.0.0.1:8000/generate")
ANALYZER_URL = os.getenv("ANALYZER_URL", "http://localhost:8001/analyze")

# Все возможные stages для генерации пайплайна со всеми этапами
ALL_STAGES = [
    "pre_checks",
    "lint",
    "type_check",
    "security",
    "test",
    "build",
    "docker_build",
    "docker_push",
    "integration",
    "migration",
    "deploy",
    "post_deploy",
    "cleanup",
]


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
    # Убираем docker_context и dockerfile_path из analysis (они не должны быть там)
    # и добавляем их в user_settings, если они есть
    analysis_dict = analysis.model_dump()
    docker_context_from_analysis = analysis_dict.pop("docker_context", None)
    dockerfile_path_from_analysis = analysis_dict.pop("dockerfile_path", None)
    
    user_settings_dict = user_settings.model_dump()
    # Добавляем docker_context и dockerfile_path в user_settings, если их там нет
    if not user_settings_dict.get("docker_context"):
        user_settings_dict["docker_context"] = docker_context_from_analysis or "."
    if not user_settings_dict.get("dockerfile_path"):
        user_settings_dict["dockerfile_path"] = dockerfile_path_from_analysis or "Dockerfile"
    
    payload = {
        "analysis": analysis_dict,
        "user_settings": user_settings_dict,
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
        project_id=payload.project_id,
        uml=uml,
    )
    return storage.create_pipeline_generation(db, create_dto)


@router.get("", response_model=list[PipelineGeneration])
async def get_pipeline_generations(db: Session = Depends(get_db)) -> list[PipelineGeneration]:
    """Получить все генерации пайплайнов."""
    return storage.list_pipeline_generations(db)


@router.post("/generate-from-repo", response_class=PlainTextResponse)
async def generate_pipeline_from_repo(
    payload: PipelineGenerateFromRepoRequest, db: Session = Depends(get_db)
) -> PlainTextResponse:
    """
    Генерирует пайплайн напрямую из репозитория со всеми возможными stages.

    Принимает:
    - repo_url — URL Git-репозитория
    - token — токен для клонирования репозитория

    Возвращает сгенерированный пайплайн со всеми возможными stages в виде YAML.
    """
    # Получаем анализ репозитория
    analysis = await fetch_analysis(str(payload.repo_url), payload.token)

    # Создаем настройки с всеми возможными stages
    user_settings = UserSettings(
        platform="gitlab",
        stages=ALL_STAGES,  # Все возможные stages
        triggers=TriggerSettings(
            on_push=["main", "master"],
            on_merge_request=False,
            on_tags="",
            schedule="",
            manual=False,
        ),
        variables={},
        docker_context=analysis.docker_context if analysis.docker else ".",
        dockerfile_path=analysis.dockerfile_path if analysis.docker else "Dockerfile",
    )

    # Генерируем пайплайн
    pipeline = await call_pipeline_generator(analysis, user_settings)

    return PlainTextResponse(content=pipeline, media_type="text/plain")

