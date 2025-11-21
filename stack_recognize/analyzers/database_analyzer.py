"""Анализатор баз данных."""
import re
import logging
from pathlib import Path

from ..models import ProjectStack
from ..config import ConfigLoader, PatternConfig

logger = logging.getLogger(__name__)


class DatabaseAnalyzer:
    """Анализатор для определения используемых баз данных."""

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
        Анализ используемых баз данных.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        # Анализ по конфигурационным файлам
        self._analyze_by_files(repo_path, stack)

        # Анализ по зависимостям и импортам
        self._analyze_by_content(repo_path, stack)

    def _analyze_by_files(self, repo_path: Path, stack: ProjectStack):
        """Анализ баз данных по наличию специфичных файлов."""
        database_files = {
            'postgresql': ['postgresql.conf', 'pg_hba.conf'],
            'mysql': ['my.cnf', 'my.ini'],
            'mongodb': ['mongod.conf'],
            'redis': ['redis.conf'],
            'sqlite': ['*.db', '*.sqlite', '*.sqlite3'],
        }

        for db, patterns in database_files.items():
            for pattern in patterns:
                if list(repo_path.rglob(pattern)):
                    if db not in stack.databases:
                        stack.databases.append(db)
                    break

    def _analyze_by_content(self, repo_path: Path, stack: ProjectStack):
        """Анализ баз данных по содержимому файлов."""
        code_extensions = ['.py', '.js', '.ts', '.java', '.php', '.rb', '.go', '.cs']

        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    for db, patterns in self.pattern_config.DATABASE_PATTERNS.items():
                        if db not in stack.databases:
                            for pattern in patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    stack.databases.append(db)
                                    break
                except (UnicodeDecodeError, IOError):
                    continue


