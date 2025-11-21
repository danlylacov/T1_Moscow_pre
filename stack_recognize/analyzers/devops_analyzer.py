"""Анализатор DevOps инструментов."""
import logging
from pathlib import Path

from ..models import ProjectStack
from ..config import ConfigLoader

logger = logging.getLogger(__name__)


class DevOpsAnalyzer:
    """Анализатор для определения DevOps инструментов."""

    def __init__(self, config_loader: ConfigLoader):
        """
        Инициализация анализатора.

        Args:
            config_loader: Загрузчик конфигурации
        """
        self.config_loader = config_loader

    def analyze(self, repo_path: Path, stack: ProjectStack):
        """
        Анализ DevOps инструментов.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        devops_files = {
            'docker': ['Dockerfile', 'Dockerfile.*', '*.dockerfile', '.dockerignore'],
            'docker-compose': ['docker-compose.yml', 'docker-compose.yaml'],
            'kubernetes': ['k8s/**/*', 'manifests/**/*', '*.yaml', '*.yml'],
            'helm': ['Chart.yaml', 'charts/**/*'],
            'terraform': ['*.tf', 'terraform/**/*', '.terraform.lock.hcl'],
            'ansible': ['ansible.cfg', 'inventory', 'playbook.yml', 'roles/**/*'],
            'pulumi': ['Pulumi.yaml', 'Pulumi.*.yaml'],
            'vagrant': ['Vagrantfile'],
        }

        detected_files = {}

        for tool, patterns in devops_files.items():
            for pattern in patterns:
                matches = list(repo_path.rglob(pattern))
                if matches:
                    if tool == 'docker':
                        stack.docker = True
                    elif tool == 'docker-compose':
                        stack.docker = True  # docker-compose тоже указывает на Docker
                    elif tool == 'kubernetes':
                        stack.kubernetes = True
                    elif tool == 'helm':
                        stack.kubernetes = True  # Helm тоже указывает на Kubernetes
                    elif tool == 'terraform':
                        stack.terraform = True

                    detected_files[tool] = [str(m.relative_to(repo_path)) for m in matches]
                    break

        stack.files_detected.update(detected_files)

