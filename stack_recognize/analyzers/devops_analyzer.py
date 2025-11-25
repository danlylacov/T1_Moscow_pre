"""Анализатор DevOps инструментов."""
import logging
from pathlib import Path
from typing import List, Optional

from ..models import ProjectStack
from ..config import ConfigLoader
from ..utils import get_relevant_files, should_ignore_path

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

    @staticmethod
    def _select_main_dockerfile(docker_files: List[Path], repo_path: Path) -> Optional[Path]:
        """Выбрать основной Dockerfile из списка по приоритету.
        
        Приоритет:
        1. Dockerfile в корне проекта
        2. Dockerfile в любой директории
        3. Dockerfile.* файлы (Dockerfile.prod, Dockerfile.dev и т.д.)
        4. *.dockerfile файлы
        
        Args:
            docker_files: Список найденных Dockerfile файлов
            repo_path: Корневой путь репозитория
            
        Returns:
            Основной Dockerfile или None
        """
        if not docker_files:
            return None
        
        # Приоритет 1: Dockerfile в корне проекта
        for f in docker_files:
            rel_path = f.relative_to(repo_path)
            if rel_path.name == 'Dockerfile' and len(rel_path.parts) == 1:
                return f
        
        # Приоритет 2: Dockerfile в любой директории
        for f in docker_files:
            rel_path = f.relative_to(repo_path)
            if rel_path.name == 'Dockerfile':
                return f
        
        # Приоритет 3: Dockerfile.* файлы (Dockerfile.prod, Dockerfile.dev и т.д.)
        dockerfile_variants = []
        for f in docker_files:
            if f.name.startswith('Dockerfile.') or f.name.startswith('Dockerfile-'):
                dockerfile_variants.append(f)
        
        if dockerfile_variants:
            # Сортируем по имени, чтобы выбрать наиболее стандартный (например, Dockerfile.prod)
            dockerfile_variants.sort(key=lambda x: x.name)
            return dockerfile_variants[0]
        
        # Приоритет 4: *.dockerfile файлы
        dockerfile_ext = [f for f in docker_files if f.name.endswith('.dockerfile')]
        if dockerfile_ext:
            dockerfile_ext.sort(key=lambda x: x.name)
            return dockerfile_ext[0]
        
        # Если ничего не подошло, возвращаем первый
        return docker_files[0]

    def analyze(self, repo_path: Path, stack: ProjectStack):
        """
        Анализ DevOps инструментов.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        devops_files = {
            'docker': ['Dockerfile', '*.dockerfile'],
            'docker-compose': ['docker-compose.yml', 'docker-compose.yaml'],
            'kubernetes': ['k8s/**/*', 'manifests/**/*'],
            'helm': ['Chart.yaml'],
            'terraform': ['*.tf', '.terraform.lock.hcl'],
            'ansible': ['ansible.cfg', 'inventory', 'playbook.yml'],
            'pulumi': ['Pulumi.yaml'],
            'vagrant': ['Vagrantfile'],
        }

        detected_files = {}
        
        # Используем оптимизированный поиск файлов
        relevant_files = get_relevant_files(repo_path)
        logger.info(f"Найдено релевантных файлов для анализа DevOps: {len(relevant_files)}")
        
        # Дополнительный поиск Dockerfile и docker-compose через rglob (на случай, если они не попали в relevant_files)
        dockerfile_matches = list(repo_path.rglob('Dockerfile*'))
        dockerfile_matches = [f for f in dockerfile_matches if f.is_file() and not should_ignore_path(f)]
        logger.info(f"Найдено Dockerfile файлов через rglob: {len(dockerfile_matches)}")
        if dockerfile_matches:
            logger.info(f"Dockerfile файлы: {[str(f.relative_to(repo_path)) for f in dockerfile_matches]}")
            before_count = len(relevant_files)
            relevant_files.extend([f for f in dockerfile_matches if f not in relevant_files])
            after_count = len(relevant_files)
            logger.info(f"Добавлено Dockerfile файлов в relevant_files: {after_count - before_count}, всего файлов: {after_count}")
        
        docker_compose_matches = list(repo_path.rglob('docker-compose.*'))
        docker_compose_matches = [f for f in docker_compose_matches if f.is_file() and not should_ignore_path(f)]
        logger.info(f"Найдено docker-compose файлов через rglob: {len(docker_compose_matches)}")
        if docker_compose_matches:
            logger.info(f"docker-compose файлы: {[str(f.relative_to(repo_path)) for f in docker_compose_matches]}")
            relevant_files.extend([f for f in docker_compose_matches if f not in relevant_files])

        # Сначала проверяем Docker и docker-compose напрямую
        # Dockerfile может быть: Dockerfile, Dockerfile.prod, Dockerfile_backend, Dockerfile-frontend и т.д.
        docker_files = []
        for f in relevant_files:
            if f.name == 'Dockerfile' or f.name.startswith('Dockerfile') or f.name.endswith('.dockerfile'):
                docker_files.append(f)
        
        logger.info(f"Найдено потенциальных Dockerfile файлов в relevant_files: {len(docker_files)}")
        if docker_files:
            logger.info(f"Имена Dockerfile файлов: {[f.name for f in docker_files]}")
            stack.docker = True
            
            # Выбираем основной Dockerfile по приоритету
            main_dockerfile = self._select_main_dockerfile(docker_files, repo_path)
            if main_dockerfile:
                # Сохраняем основной Dockerfile в ключе 'docker'
                detected_files['docker'] = [str(main_dockerfile.relative_to(repo_path))]
                # Все остальные Dockerfile сохраняем в 'docker_all' для справки
                all_dockerfiles = [str(f.relative_to(repo_path)) for f in docker_files]
                if len(all_dockerfiles) > 1:
                    detected_files['docker_all'] = all_dockerfiles
                logger.info(f"Выбран основной Dockerfile: {main_dockerfile.relative_to(repo_path)}")
                logger.info(f"Обнаружен Docker: {detected_files['docker']}")
            else:
                detected_files['docker'] = [str(f.relative_to(repo_path)) for f in docker_files]
                logger.info(f"Обнаружен Docker: {detected_files['docker']}")
        
        docker_compose_files = [f for f in relevant_files 
                               if f.name in ['docker-compose.yml', 'docker-compose.yaml']]
        if docker_compose_files:
            stack.docker = True  # docker-compose тоже указывает на Docker
            detected_files['docker-compose'] = [str(f.relative_to(repo_path)) for f in docker_compose_files]
            logger.info(f"Обнаружен docker-compose: {detected_files['docker-compose']}")
        
        # Обработка остальных инструментов
        for tool, patterns in devops_files.items():
            if tool in ['docker', 'docker-compose']:
                continue  # Уже обработали выше
            
            for pattern in patterns:
                matches = []
                
                # Обработка разных типов паттернов
                if pattern.startswith('*.') and pattern != '*.dockerfile':
                    # Файлы с определенным расширением
                    ext = pattern[1:]  # убираем *
                    matches = [f for f in relevant_files 
                              if f.name.endswith(ext)]
                elif '**' in pattern:
                    # Паттерны с ** - ищем в поддиректориях
                    dir_part = pattern.split('/')[0]
                    matches = [f for f in relevant_files 
                              if dir_part in str(f.relative_to(repo_path))]
                else:
                    # Точное совпадение имени файла
                    matches = [f for f in relevant_files if f.name == pattern]
                
                if matches:
                    if tool == 'kubernetes':
                        stack.kubernetes = True
                    elif tool == 'helm':
                        stack.kubernetes = True  # Helm тоже указывает на Kubernetes
                    elif tool == 'terraform':
                        stack.terraform = True

                    detected_files[tool] = [str(m.relative_to(repo_path)) for m in matches]
                    break

        stack.files_detected.update(detected_files)

