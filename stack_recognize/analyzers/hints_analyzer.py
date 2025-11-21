"""Анализатор дополнительных подсказок о проекте."""
import logging
from pathlib import Path

from ..models import ProjectStack
from ..config import ConfigLoader

logger = logging.getLogger(__name__)


class HintsAnalyzer:
    """Анализатор для определения дополнительных подсказок о проекте."""

    def __init__(self, config_loader: ConfigLoader):
        """
        Инициализация анализатора.

        Args:
            config_loader: Загрузчик конфигурации
        """
        self.config_loader = config_loader

    def analyze(self, repo_path: Path, stack: ProjectStack):
        """
        Анализ дополнительных подсказок о проекте.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        hint_files = {
            'Наличие конфигурации веб-сервера': ['nginx.conf', 'apache.conf', '.htaccess', 'httpd.conf'],
            'Наличие конфигурации базы данных': ['*.sql', 'migrations/**/*', 'seeders/**/*'],
            'Наличие документации': ['README.md', 'docs/**/*', '*.md', 'CHANGELOG.md', 'CONTRIBUTING.md'],
            'Наличие линтеров': ['.eslintrc', '.pylintrc', 'phpcs.xml', '.rubocop.yml', '.prettierrc'],
            'Наличие форматеров': ['.editorconfig', '.prettierrc', '.prettierignore'],
            'Наличие мониторинга': ['prometheus.yml', 'grafana.ini', 'newrelic.ini'],
            'Наличие контейнеризации': ['.dockerignore', 'compose.yaml'],
            'Наличие оркестрации': ['kustomization.yaml', 'values.yaml'],
        }

        for hint, patterns in hint_files.items():
            for pattern in patterns:
                if list(repo_path.rglob(pattern)):
                    stack.hints.append(hint)
                    break

