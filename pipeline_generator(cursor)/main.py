from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from ci_generator.generate import generate_pipeline


app = FastAPI(
    title="CI/CD Pipeline Generator API",
    description="FastAPI-обёртка над генератором GitLab CI/CD пайплайнов",
    version="1.0.0",
)


class EntryPoint(BaseModel):
    path: str
    type: str
    lang: Optional[str] = None
    confidence: float


class MainEntry(BaseModel):
    path: str
    type: str
    lang: str
    confidence: float


class AnalysisModel(BaseModel):
    languages: List[str]
    frameworks: List[str]
    frontend_frameworks: List[str]
    backend_frameworks: List[str]
    package_manager: str
    test_runner: str
    docker: bool
    kubernetes: bool
    terraform: bool
    databases: List[str]
    entry_points: List[EntryPoint]
    main_entry: MainEntry


class TriggersModel(BaseModel):
    on_push: List[str] = Field(default_factory=list)
    on_merge_request: bool = False
    on_tags: str = ""
    schedule: str = ""
    manual: bool = False


class UserSettingsModel(BaseModel):
    platform: str = "gitlab"
    triggers: TriggersModel
    stages: List[str]
    docker_registry: Optional[str] = None
    docker_image: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)


class GenerateRequest(BaseModel):
    analysis: AnalysisModel
    user_settings: UserSettingsModel


class RequiredVariableResponse(BaseModel):
    name: str
    description: Optional[str] = None
    required: Optional[bool] = None
    default_value: Optional[Any] = None
    example: Optional[Any] = None
    job_usage: Optional[List[str]] = None


class GenerateResponse(BaseModel):
    yaml: str
    required_variables: List[RequiredVariableResponse]


@app.post("/generate", response_model=GenerateResponse)
def generate_ci_pipeline(payload: GenerateRequest) -> GenerateResponse:
    """
    Сгенерировать GitLab CI/CD пайплайн.

    Вход:
    - analysis: JSON с анализом репозитория
    - user_settings: JSON с пользовательскими настройками

    Выход:
    - yaml: строка с содержимым .gitlab-ci.yml
    - required_variables: список необходимых переменных и их описаний
    """
    yaml_content, _explanation, _validation, required_variables = generate_pipeline(
        payload.analysis.model_dump(),
        payload.user_settings.model_dump(),
    )

    required_vars_serialized = [
        {
            "name": v.name,
            "description": getattr(v, "description", None),
            "required": getattr(v, "required", None),
            "default_value": getattr(v, "default_value", None),
            "example": getattr(v, "example", None),
            "job_usage": getattr(v, "job_usage", None),
        }
        for v in required_variables
    ]

    return GenerateResponse(
        yaml=yaml_content,
        required_variables=required_vars_serialized,  # type: ignore[arg-type]
    )

