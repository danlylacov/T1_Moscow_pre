"""Вспомогательные функции для проекта."""
import re
from typing import Optional
from pathlib import Path


def get_language_by_extension(extension: str) -> Optional[str]:
    """Определение языка по расширению файла."""
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'javascript',  # TypeScript использует те же паттерны
        '.java': 'java',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.cs': 'java',  # C# использует похожие паттерны как Java
    }
    return language_map.get(extension)


def detect_language_from_command(command: str) -> str:
    """Определение языка из команды."""
    if 'node' in command:
        return 'javascript'
    elif 'python' in command:
        return 'python'
    elif 'java' in command:
        return 'java'
    elif 'php' in command:
        return 'php'
    elif 'ruby' in command:
        return 'ruby'
    return 'unknown'


def get_language_extensions() -> dict:
    """Получить словарь расширений файлов по языкам."""
    return {
        # Основные языки
        'python': ['.py', '.pyw'],
        'javascript': ['.js'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'go': ['.go'],
        'ruby': ['.rb'],
        'php': ['.php'],
        'rust': ['.rs'],
        'csharp': ['.cs'],
        'cpp': ['.cpp', '.cxx', '.cc', '.c'],
        'c': ['.c'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts'],
        'scala': ['.scala'],
        'haskell': ['.hs'],
        'elixir': ['.ex', '.exs'],
        'clojure': ['.clj', '.cljs'],
        'erlang': ['.erl'],
        'perl': ['.pl', '.pm'],
        'lua': ['.lua'],
        'r': ['.r'],
        'matlab': ['.m'],
        'dart': ['.dart'],
        'fsharp': ['.fs', '.fsx'],
        'vbnet': ['.vb'],
        'objective-c': ['.m', '.mm'],
        'assembly': ['.asm', '.s'],
        # Веб-технологии
        'html': ['.html', '.htm'],
        'css': ['.css', '.scss', '.sass', '.less'],
        'xml': ['.xml'],
        'json': ['.json'],
        'yaml': ['.yaml', '.yml'],
        'markdown': ['.md', '.markdown'],
        # Конфигурационные файлы
        'shell': ['.sh', '.bash', '.zsh'],
        'powershell': ['.ps1'],
        'batch': ['.bat', '.cmd'],
        'makefile': ['Makefile'],
        'dockerfile': ['Dockerfile'],
    }

