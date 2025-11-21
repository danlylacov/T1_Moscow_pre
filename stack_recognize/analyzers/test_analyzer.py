"""Анализатор тестовых раннеров."""
import re
import logging
from pathlib import Path

from ..models import ProjectStack
from ..config import ConfigLoader, PatternConfig

logger = logging.getLogger(__name__)


class TestAnalyzer:
    """Анализатор для определения тестовых раннеров."""

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
        Анализ тестовых раннеров.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        # Анализ по файлам
        self._analyze_by_files(repo_path, stack)

        # Анализ по содержимому файлов
        if not stack.test_runner:
            self._analyze_by_content(repo_path, stack)

    def _analyze_by_files(self, repo_path: Path, stack: ProjectStack):
        """Анализ тестовых раннеров по наличию специфичных файлов."""
        test_files = {
            'pytest': ['pytest.ini', 'pyproject.toml', 'tox.ini', 'conftest.py', '**/test_*.py', '**/*_test.py'],
            'unittest': ['**/test_*.py', '**/*_test.py'],
            'jest': ['jest.config.js', 'jest.config.ts', 'jest.config.json'],
            'mocha': ['.mocharc.js', '.mocharc.json', '.mocharc.yaml'],
            'jasmine': ['jasmine.json', 'spec/support/jasmine.json'],
            'karma': ['karma.conf.js', 'karma.conf.ts'],
            'cypress': ['cypress.json', 'cypress.config.js', 'cypress/', 'cypress.env.json'],
            'playwright': ['playwright.config.js', 'playwright.config.ts'],
            'phpunit': ['phpunit.xml', 'phpunit.xml.dist'],
            'rspec': ['.rspec', 'spec_helper.rb'],
            'cucumber': ['cucumber.yml', 'cucumber.js', 'features/**/*.feature'],
        }

        for runner, patterns in test_files.items():
            for pattern in patterns:
                if list(repo_path.rglob(pattern)):
                    stack.test_runner = runner
                    return

    def _analyze_by_content(self, repo_path: Path, stack: ProjectStack):
        """Анализ тестовых раннеров по содержимому файлов."""
        code_extensions = ['.py', '.js', '.ts', '.java', '.php', '.rb', '.feature']

        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    for runner, patterns in self.pattern_config.TEST_RUNNER_PATTERNS.items():
                        if not stack.test_runner:
                            for pattern in patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    stack.test_runner = runner
                                    return
                except (UnicodeDecodeError, IOError):
                    continue


