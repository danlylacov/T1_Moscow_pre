#!/usr/bin/env python3
"""
main_generator.py

Запуск генерации: читает JSON input -> выбирает стадии -> рендерит pipeline для выбранной платформы.
"""

import sys
import json
from pathlib import Path

# Используем относительные импорты, чтобы модуль корректно работал при запуске
# через `python -m generator.main_generator` из корня проекта.
from .stage_selector import select_stages
from .renderer import PipelineRenderer

def load_input(path=None):
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return json.load(sys.stdin)

def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) == 0:
        print("Usage: python -m generator.main_generator example/example_input.json [gitlab|jenkins]")
        sys.exit(1)

    input_path = argv[0]
    platform = argv[1] if len(argv) > 1 else None

    data = load_input(input_path)
    analysis = data.get("analysis", {})
    user_settings = data.get("user_settings", {})

    # platform preference: CLI arg > user_settings > default gitlab
    platform = (platform or user_settings.get("platform") or "gitlab").lower()

    stages = select_stages(analysis, user_settings)

    ctx = {
        "project_name": user_settings.get("project_name", "myapp"),
        "python_version": user_settings.get("python_version", analysis.get("python_version", "3.11")),
        "registry": user_settings.get("docker_registry", analysis.get("docker_registry", "$CI_REGISTRY")),
        "tag": user_settings.get("docker_tag", "$CI_COMMIT_SHORT_SHA"),
        "variables": user_settings.get("variables", {}),
        "triggers": user_settings.get("triggers", {}),
        # Docker-путь теперь приходит из analysis и используется только если docker == true
        "docker_context": (analysis.get("docker_context") or ".") if analysis.get("docker") else ".",
        "dockerfile_path": (analysis.get("dockerfile_path") or "Dockerfile") if analysis.get("docker") else "Dockerfile",
        "analysis": analysis,
        "user_settings": user_settings,
    }

    base_dir = Path(__file__).resolve().parents[1] / "pipelines"

    renderer = PipelineRenderer(templates_root=str(base_dir))

    if platform == "gitlab":
        out = renderer.render_gitlab(stages, ctx)
    elif platform == "jenkins":
        out = renderer.render_jenkins(stages, ctx)
    else:
        raise SystemExit(f"Unsupported platform: {platform}")

    print(out)


if __name__ == "__main__":
    main()
