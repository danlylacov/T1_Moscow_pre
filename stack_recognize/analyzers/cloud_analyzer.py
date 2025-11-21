"""Анализатор облачных платформ."""
import re
import logging
from pathlib import Path

from ..models import ProjectStack
from ..config import ConfigLoader, PatternConfig

logger = logging.getLogger(__name__)


class CloudAnalyzer:
    """Анализатор для определения облачных платформ."""

    def __init__(self, config_loader: ConfigLoader):
        """
        Инициализация анализатора.

        Args:
            config_loader: Загрузчик конфигурации
        """
        self.config_loader = config_loader
        self.pattern_config = PatternConfig()

    def analyze(self, repo_path: Path, stack: ProjectStack):
        """
        Анализ облачных платформ.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        # Анализ по конфигурационным файлам
        self._analyze_by_files(repo_path, stack)

        # Анализ по зависимостям и импортам
        self._analyze_by_content(repo_path, stack)

    def _analyze_by_files(self, repo_path: Path, stack: ProjectStack):
        """Анализ облачных платформ по наличию специфичных файлов."""
        cloud_files = {
            'aws': ['.aws/', 'aws.yml', 'aws.yaml'],
            'azure': ['.azure/', 'azure-pipelines.yml'],
            'gcp': ['.gcp/', 'gcp.yaml', 'app.yaml'],
            'heroku': ['Procfile', 'app.json'],
        }

        for cloud, patterns in cloud_files.items():
            for pattern in patterns:
                if list(repo_path.rglob(pattern)):
                    if cloud not in stack.cloud_platforms:
                        stack.cloud_platforms.append(cloud)
                    break

    def _analyze_by_content(self, repo_path: Path, stack: ProjectStack):
        """Анализ облачных платформ по содержимому файлов."""
        code_extensions = ['.py', '.js', '.ts', '.java', '.php', '.rb', '.go', '.cs', '.yaml', '.yml']

        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    for cloud, patterns in self.pattern_config.CLOUD_PATTERNS.items():
                        if cloud not in stack.cloud_platforms:
                            for pattern in patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    stack.cloud_platforms.append(cloud)
                                    break
                except (UnicodeDecodeError, IOError):
                    continue


