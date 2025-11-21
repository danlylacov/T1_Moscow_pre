"""
plugins/technologies/kubernetes.py
"""

K8S_STAGES = [
    "deploy",
    "post_deploy",
]

def enabled(analysis: dict) -> bool:
    return bool(analysis.get("kubernetes"))

def get_stages(analysis: dict, user_settings: dict):
    return list(K8S_STAGES)
