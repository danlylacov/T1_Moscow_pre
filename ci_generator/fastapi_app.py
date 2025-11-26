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
    java_version: Optional[str] = None
    go_version: Optional[str] = None
    node_version: Optional[str] = None
    build_tool: Optional[str] = None
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

    # Определяем build_tool для Java на основе package_manager
    build_tool = None
    if "java" in analysis_dict.get("languages", []):
        package_manager = analysis_dict.get("package_manager", "").lower()
        if package_manager in ["maven", "gradle"]:
            build_tool = package_manager
        elif package_manager == "ant":
            build_tool = "ant"
        else:
            # По умолчанию для Java используем maven
            build_tool = user_settings_dict.get("build_tool", "maven")

    # Определяем основной язык программирования
    languages = [l.lower() for l in analysis_dict.get("languages", [])]
    main_languages = ["python", "java", "kotlin", "go", "golang", "typescript", "javascript"]
    language = None
    for lang in languages:
        if lang in main_languages:
            language = lang
            break
    # Если язык не найден, берем первый из списка или используем python по умолчанию
    if not language and languages:
        language = languages[0]
    elif not language:
        language = "python"

    # Контекст для шаблонов - добавляем версии только для используемого языка
    ctx = {
        "language": language,
        "project_name": user_settings_dict.get("project_name", "myapp"),
        "build_tool": build_tool or user_settings_dict.get("build_tool"),
    }
    
    # Добавляем версию только для используемого языка
    if language == "python":
        ctx["python_version"] = user_settings_dict.get("python_version", analysis_dict.get("python_version", "3.11"))
    elif language in ["java", "kotlin"]:
        ctx["java_version"] = user_settings_dict.get("java_version", analysis_dict.get("java_version", "17"))
    elif language in ["go", "golang"]:
        ctx["go_version"] = user_settings_dict.get("go_version", analysis_dict.get("go_version", "1.21"))
    elif language in ["typescript", "javascript"]:
        ctx["node_version"] = user_settings_dict.get("node_version", analysis_dict.get("node_version", "18"))
    
    # Добавляем build_image для Java/Kotlin
    if language in ["java", "kotlin"]:
        ctx["build_image"] = user_settings_dict.get("build_image") or (
            f"maven:{user_settings_dict.get('java_version', analysis_dict.get('java_version', '17'))}-eclipse-temurin" 
            if language in ["java", "kotlin"] and (build_tool or user_settings_dict.get("build_tool") or "maven") == "maven"
            else f"gradle:{user_settings_dict.get('java_version', analysis_dict.get('java_version', '17'))}-jdk"
            if language in ["java", "kotlin"] and (build_tool or user_settings_dict.get("build_tool")) == "gradle"
            else None
        )
    
    # Добавляем остальные общие поля
    ctx.update({
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
    })

    templates_root = Path(__file__).resolve().parent / "pipelines"
    renderer = PipelineRenderer(templates_root=str(templates_root))

    if platform == "gitlab":
        out = renderer.render_gitlab(stages, ctx)
    elif platform == "jenkins":
        out = renderer.render_jenkins(stages, ctx)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    return PlainTextResponse(content=out, media_type="text/plain")



