"""
plugins/technologies/docker.py
"""

DOCKER_STAGES = [
    "docker_build",
    "docker_push",
    "cleanup",
    "integration",   # integration often uses docker-compose
]

def enabled(analysis: dict) -> bool:
    return bool(analysis.get("docker"))

def get_stages(analysis: dict, user_settings: dict):
    stages = list(DOCKER_STAGES)
    # only include push if registry provided
    registry = user_settings.get("docker_registry") or user_settings.get("docker_image") or ""
    if not registry and "docker_push" in stages:
        stages.remove("docker_push")
    # include integration only if entry_points include docker-compose
    has_compose = any((e.get("type") and "docker-compose" in str(e.get("type"))) for e in analysis.get("entry_points",[]))
    if not has_compose and "integration" in stages:
        stages.remove("integration")
    return stages
