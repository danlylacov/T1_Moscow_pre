from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, HttpUrl, Field


# ---------- Пользователь ----------


class UserBase(BaseModel):
    username: str = Field(..., description="Логин пользователя")


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, description="Пароль в открытом виде (НЕ для продакшена)")


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Проект и анализ репозитория ----------


class EntryPoint(BaseModel):
    path: str
    type: str
    lang: Optional[str] = None
    confidence: float


class ProjectAnalysis(BaseModel):
    languages: List[str] = []
    frameworks: List[str] = []
    frontend_frameworks: List[str] = []
    backend_frameworks: List[str] = []
    package_manager: Optional[str] = None
    test_runner: Optional[str] = None
    docker: bool = False
    docker_context: str = ""
    dockerfile_path: Optional[str] = None
    kubernetes: bool = False
    terraform: bool = False
    databases: List[str] = []
    entry_points: List[EntryPoint] = []
    main_entry: Optional[EntryPoint] = None


class ProjectBase(BaseModel):
    name: str = Field(..., description="Название проекта в Self-Deploy")
    url: HttpUrl = Field(..., description="URL Git-репозитория")
    clone_token: str = Field(..., description="Токен для клонирования репозитория")
    user_id: int = Field(..., description="ID владельца проекта")


class ProjectCreate(ProjectBase):
    analysis: Optional[ProjectAnalysis] = None


class ProjectCreateRequest(ProjectBase):
    """
    Входная схема для создания проекта от клиента.
    Анализ репозитория заполняется автоматически через внешний сервис.
    """


class Project(ProjectBase):
    id: int
    analysis: Optional[ProjectAnalysis] = None

    class Config:
        from_attributes = True


# ---------- Генерация пайплайна ----------


class PipelineGenerationBase(BaseModel):
    user_id: int
    project_id: Optional[int] = None
    uml: str = Field(..., description="Готовый пайплайн в UML-представлении или другом форматировании")


class PipelineGenerationCreate(PipelineGenerationBase):
    ...


class PipelineGeneration(PipelineGenerationBase):
    id: int
    generated_at: datetime

    class Config:
        from_attributes = True



# ---------- Пользовательские настройки для генерации пайплайна ----------


class TriggerSettings(BaseModel):
    on_push: List[str] = []
    on_merge_request: bool = False
    on_tags: str | None = ""
    schedule: str | None = ""
    manual: bool = False


class UserSettings(BaseModel):
    platform: str
    triggers: TriggerSettings
    stages: List[str] = []
    docker_registry: str | None = ""
    docker_image: str | None = ""
    variables: dict = {}
    project_name: str | None = ""
    python_version: str | None = ""
    docker_tag: str | None = ""


class PipelineGenerationRequest(BaseModel):
    """
    Вход для генерации пайплайна:
    - project_id: из него берётся analysis из БД
    - user_settings: пользовательские настройки генерации
    """

    user_id: int
    project_id: int
    user_settings: UserSettings



