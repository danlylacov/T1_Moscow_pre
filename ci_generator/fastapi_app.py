"""
fastapi_app.py

Обёртка над генератором CI на FastAPI.

POST /generate
- вход: JSON строго типизированный, как input.json (analysis + user_settings)
- выход: сгенерированный пайплайн (по умолчанию GitLab CI YAML как текст)
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, ConfigDict

from generator.stage_selector import select_stages
from generator.renderer import PipelineRenderer


# -------------------------
# Pydantic-модели под input.json
# -------------------------


class EntryPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    type: Optional[str] = None
    lang: Optional[str] = None
    confidence: float


class Analysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    frontend_frameworks: List[str] = Field(default_factory=list)
    backend_frameworks: List[str] = Field(default_factory=list)
    package_manager: Optional[str] = None
    test_runner: Optional[str] = None
    docker: bool = False
    kubernetes: bool = False
    terraform: bool = False
    databases: List[str] = Field(default_factory=list)
    entry_points: List[EntryPoint] = Field(default_factory=list)
    main_entry: Optional[EntryPoint] = None


class Triggers(BaseModel):
    model_config = ConfigDict(extra="forbid")

    on_push: List[str] = Field(default_factory=list)
    on_merge_request: bool = False
    on_tags: str = ""
    schedule: str = ""
    manual: bool = False


class UserSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Optional[str] = None
    triggers: Triggers = Field(default_factory=Triggers)
    stages: List[str] = Field(default_factory=list)
    docker_registry: Optional[str] = None
    docker_image: Optional[str] = None
    docker_context: str = "."
    dockerfile_path: str = "Dockerfile"
    variables: Dict[str, Any] = Field(default_factory=dict)
    project_name: Optional[str] = None
    python_version: Optional[str] = None
    docker_tag: Optional[str] = None


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis: Analysis
    user_settings: UserSettings


# -------------------------
# FastAPI app
# -------------------------


app = FastAPI(title="CI Pipeline Generator API")


@app.post("/generate", response_class=PlainTextResponse)
def generate_pipeline(req: GenerateRequest) -> PlainTextResponse:
    """
    Принимает JSON как input.json и возвращает сгенерированный пайплайн.
    По умолчанию платформа gitlab (можно переопределить user_settings.platform).
    """
    analysis_dict = req.analysis.model_dump()
    user_settings_dict = req.user_settings.model_dump()

    # Логика выбора платформы как в main_generator.py:
    platform = (user_settings_dict.get("platform") or "gitlab").lower()

    # Выбор стадий
    stages = select_stages(analysis_dict, user_settings_dict)

    # Контекст для шаблонов
    ctx = {
        "project_name": user_settings_dict.get("project_name", "myapp"),
        "python_version": user_settings_dict.get(
            "python_version", analysis_dict.get("python_version", "3.11")
        ),
        "registry": user_settings_dict.get(
            "docker_registry", analysis_dict.get("docker_registry", "$CI_REGISTRY")
        ),
        "tag": user_settings_dict.get("docker_tag", "$CI_COMMIT_SHORT_SHA"),
        "variables": user_settings_dict.get("variables", {}),
        "triggers": user_settings_dict.get("triggers", {}),
        "docker_context": user_settings_dict.get("docker_context", "."),
        "dockerfile_path": user_settings_dict.get("dockerfile_path", "Dockerfile"),
        "analysis": analysis_dict,
        "user_settings": user_settings_dict,
    }

    templates_root = Path(__file__).resolve().parent / "pipelines"
    renderer = PipelineRenderer(templates_root=str(templates_root))

    if platform == "gitlab":
        out = renderer.render_gitlab(stages, ctx)
    elif platform == "jenkins":
        out = renderer.render_jenkins(stages, ctx)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    return PlainTextResponse(content=out, media_type="text/plain")



