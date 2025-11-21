"""Анализатор фреймворков."""
import re
import logging
from pathlib import Path

from ..models import ProjectStack
from ..config import ConfigLoader, PatternConfig

logger = logging.getLogger(__name__)


class FrameworkAnalyzer:
    """Анализатор для определения фреймворков."""

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
        Анализ фреймворков.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        # Анализ по файлам
        self._analyze_by_files(repo_path, stack)

        # Анализ по содержимому файлов
        self._analyze_by_content(repo_path, stack)

        # Классификация фреймворков
        self._classify_frameworks(stack)

    def _analyze_by_files(self, repo_path: Path, stack: ProjectStack):
        """Анализ фреймворков по наличию специфичных файлов."""
        framework_files = {
            'django': ['manage.py', 'wsgi.py', 'asgi.py'],
            'flask': ['app.py', 'application.py', 'wsgi.py'],
            'fastapi': ['main.py'],
            'laravel': ['artisan', 'server.php'],
            'rails': ['bin/rails', 'config/application.rb', 'config.ru'],
            'symfony': ['symfony.lock', 'bin/console'],
            'spring-boot': ['pom.xml', 'build.gradle', 'application.properties'],
            'aspnet-core': ['.csproj', 'Startup.cs', 'Program.cs'],
            'flutter': ['pubspec.yaml', 'lib/main.dart'],
            'react-native': ['index.js', 'App.js', 'metro.config.js'],
            'ionic': ['ionic.config.json'],
            'electron': ['electron.js', 'main.js'],
            'nextjs': ['next.config.js'],
            'nuxt': ['nuxt.config.js'],
            'gatsby': ['gatsby-config.js'],
            'quarkus': ['pom.xml', 'application.properties'],
            'micronaut': ['micronaut-cli.yml'],
        }

        for framework, files in framework_files.items():
            for pattern in files:
                if list(repo_path.rglob(pattern)):
                    if framework not in stack.frameworks:
                        stack.frameworks.append(framework)
                    break

    def _analyze_by_content(self, repo_path: Path, stack: ProjectStack):
        """Анализ фреймворков по содержимому файлов."""
        code_extensions = ['.py', '.js', '.ts', '.tsx', '.java', '.php', '.rb', '.go', '.rs', '.cs', '.dart', '.swift',
                           '.kt']

        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    for framework, patterns in self.pattern_config.FRAMEWORK_PATTERNS.items():
                        if framework not in stack.frameworks:
                            for pattern in patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    stack.frameworks.append(framework)
                                    break
                except (UnicodeDecodeError, IOError):
                    continue

    def _classify_frameworks(self, stack: ProjectStack):
        """Классификация фреймворков по типам."""
        for framework in stack.frameworks:
            if framework in self.pattern_config.FRONTEND_FRAMEWORKS:
                if framework not in stack.frontend_frameworks:
                    stack.frontend_frameworks.append(framework)
            elif framework in self.pattern_config.BACKEND_FRAMEWORKS:
                if framework not in stack.backend_frameworks:
                    stack.backend_frameworks.append(framework)
            elif framework in self.pattern_config.MOBILE_FRAMEWORKS:
                if framework not in stack.mobile_frameworks:
                    stack.mobile_frameworks.append(framework)

