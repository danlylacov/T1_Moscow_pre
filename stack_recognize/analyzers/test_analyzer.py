"""Анализатор тестовых раннеров."""
import re
import logging
from pathlib import Path

from ..models import ProjectStack
from ..config import ConfigLoader, PatternConfig
from ..utils import get_relevant_files, read_file_sample, get_language_by_extension

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
        # Продолжаем поиск, чтобы найти тестовые раннеры для всех языков
        self._analyze_by_content(repo_path, stack)

    def _analyze_by_files(self, repo_path: Path, stack: ProjectStack):
        """Анализ тестовых раннеров по наличию специфичных файлов."""
        test_files = {
            # Убрали 'pyproject.toml' из pytest - слишком общий файл
            'pytest': ['pytest.ini', 'tox.ini', 'conftest.py'],
            'jest': ['jest.config.js', 'jest.config.ts', 'jest.config.json'],
            'mocha': ['.mocharc.js', '.mocharc.json', '.mocharc.yaml'],
            'jasmine': ['jasmine.json'],
            'karma': ['karma.conf.js', 'karma.conf.ts'],
            'cypress': ['cypress.json', 'cypress.config.js', 'cypress.env.json'],
            'playwright': ['playwright.config.js', 'playwright.config.ts'],
            'phpunit': ['phpunit.xml', 'phpunit.xml.dist'],
            'rspec': ['.rspec'],
            'cucumber': ['cucumber.yml', 'cucumber.js'],
        }

        # Используем оптимизированный поиск файлов
        relevant_files = get_relevant_files(repo_path)
        for runner, patterns in test_files.items():
            for pattern in patterns:
                matches = [f for f in relevant_files if f.name == pattern]
                if matches:
                    if runner not in stack.test_runner:
                        stack.test_runner.append(runner)
                        logger.info(f"Обнаружен тестовый раннер {runner} по файлу: {pattern}")
                    # Не возвращаемся, продолжаем поиск для других языков

    def _analyze_by_content(self, repo_path: Path, stack: ProjectStack):
        """Анализ тестовых раннеров по содержимому файлов."""
        # Только расширения поддерживаемых языков: Python, TypeScript, Java/Kotlin, Go
        code_extensions = ['.py', '.pyw', '.ts', '.tsx', '.java', '.kt', '.kts', '.go']

        # Используем оптимизированную функцию для получения релевантных файлов
        relevant_files = get_relevant_files(repo_path, extensions=code_extensions, max_file_size=200 * 1024)

        for file_path in relevant_files:
            # Читаем только начало файла (достаточно для поиска паттернов тестов)
            content = read_file_sample(file_path, max_lines=50, max_bytes=4096)

            if not content:
                continue

            # Определяем язык файла по расширению
            file_lang = get_language_by_extension(file_path.suffix)
            
            for runner, patterns in self.pattern_config.TEST_RUNNER_PATTERNS.items():
                # Пропускаем, если этот раннер уже найден
                if runner in stack.test_runner:
                    continue
                
                # Проверка совместимости языка файла и тестового раннера
                # Python тестовые раннеры применяются только к Python файлам
                python_runners = {'pytest', 'unittest'}
                if runner in python_runners and file_lang != 'python':
                    continue
                
                # JavaScript/TypeScript тестовые раннеры применяются только к TypeScript файлам
                js_runners = {'jest', 'mocha', 'jasmine', 'karma', 'cypress', 'playwright'}
                if runner in js_runners and file_lang != 'typescript':
                    continue
                
                # Java/Kotlin тестовые раннеры применяются только к Java/Kotlin файлам
                java_runners = {'junit', 'testng'}
                if runner in java_runners and file_lang != 'java':
                    continue
                
                # PHP тестовые раннеры - не поддерживаются (нет PHP в списке языков)
                if runner == 'phpunit':
                    continue
                
                # Ruby тестовые раннеры - не поддерживаются (нет Ruby в списке языков)
                if runner == 'rspec':
                    continue
                
                # Go не имеет специфичных тестовых раннеров в списке
                # E2E/BDD тестовые раннеры могут быть в любом языке
                
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        stack.test_runner.append(runner)
                        logger.info(f"Обнаружен тестовый раннер {runner} в файле {file_path.relative_to(repo_path)} по паттерну: {pattern}")
                        break  # Переходим к следующему раннеру, не выходим из цикла
