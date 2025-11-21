"""Анализатор CI/CD конфигураций."""
import logging
from pathlib import Path

from ..models import ProjectStack
from ..config import ConfigLoader

logger = logging.getLogger(__name__)


class CICDAnalyzer:
    """Анализатор для определения CI/CD конфигураций."""

    def __init__(self, config_loader: ConfigLoader):
        """
        Инициализация анализатора.

        Args:
            config_loader: Загрузчик конфигурации
        """
        self.config_loader = config_loader

    def analyze(self, repo_path: Path, stack: ProjectStack):
        """
        Анализ CI/CD конфигураций.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        cicd_files = {
            'github-actions': ['.github/workflows/*.yml', '.github/workflows/*.yaml'],
            'gitlab': ['.gitlab-ci.yml'],
            'jenkins': ['Jenkinsfile'],
            'bitbucket': ['bitbucket-pipelines.yml'],
            'azure-pipelines': ['azure-pipelines.yml'],
            'circleci': ['.circleci/config.yml'],
            'travis': ['.travis.yml'],
            'teamcity': ['.teamcity/'],
            'bamboo': ['bamboo-specs/'],
        }

        detected_files = {}

        for provider, patterns in cicd_files.items():
            for pattern in patterns:
                matches = list(repo_path.rglob(pattern))
                if matches:
                    stack.cicd.append(provider)
                    detected_files[f'cicd_{provider}'] = [str(m.relative_to(repo_path)) for m in matches]
                    break

        stack.files_detected.update(detected_files)


