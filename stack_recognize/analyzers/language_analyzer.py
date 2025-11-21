"""Анализатор языков программирования и менеджеров пакетов."""
import json
import logging
from pathlib import Path
from typing import Dict

from ..models import ProjectStack
from ..config import ConfigLoader
from ..utils import get_language_extensions

logger = logging.getLogger(__name__)


class LanguageAnalyzer:
    """Анализатор для определения языков программирования и менеджеров пакетов."""

    def __init__(self, config_loader: ConfigLoader):
        """
        Инициализация анализатора.

        Args:
            config_loader: Загрузчик конфигурации
        """
        self.config_loader = config_loader
        self.language_extensions = get_language_extensions()

    def analyze(self, repo_path: Path, stack: ProjectStack):
        """
        Анализ языков программирования и менеджеров пакетов.

        Args:
            repo_path: Путь к репозиторию
            stack: Объект ProjectStack для заполнения
        """
        detected_files = {}

        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                filename = file_path.name
                file_path_str = str(file_path.relative_to(repo_path))

                # Определение языков по расширениям файлов
                for language, extensions in self.language_extensions.items():
                    if filename in extensions or (file_path.suffix and file_path.suffix.lower() in extensions):
                        self._add_language(language, stack)
                        key = f'{language}_files'
                        detected_files[key] = detected_files.get(key, []) + [file_path_str]

                # Определение менеджеров пакетов и сборщиков
                self._detect_package_manager(filename, file_path, repo_path, stack, detected_files)

        stack.files_detected.update(detected_files)

    def _detect_package_manager(self, filename: str, file_path: Path, repo_path: Path, stack: ProjectStack, detected_files: Dict):
        """Определение менеджера пакетов по имени файла."""
        package_manager_map = {
            'requirements.txt': ('pip', 'requirements_txt'),
            'pyproject.toml': ('poetry', 'pyproject_toml'),
            'setup.py': ('setuptools', 'setup_py'),
            'go.mod': ('go mod', 'go_mod'),
            'pom.xml': ('maven', 'pom_xml'),
            'build.gradle': ('gradle', 'build_gradle'),
            'build.gradle.kts': ('gradle', 'build_gradle_kts'),
            'composer.json': ('composer', 'composer_json'),
            'Cargo.toml': ('cargo', 'cargo_toml'),
            'Gemfile': ('bundler', 'gemfile'),
            'mix.exs': ('mix', 'mix_exs'),
            'pubspec.yaml': ('pub', 'pubspec_yaml'),
            'Podfile': ('cocoapods', 'podfile'),
            'Cartfile': ('carthage', 'cartfile'),
            'Package.swift': ('swift package manager', 'package_swift'),
        }

        if filename in package_manager_map:
            pm_name, file_key = package_manager_map[filename]
            if filename == 'package.json':
                # package.json требует специальной обработки
                self._analyze_package_json(file_path, stack)
            elif not stack.package_manager:
                stack.package_manager = pm_name
            detected_files[file_key] = str(file_path.relative_to(repo_path))

    def _analyze_package_json(self, file_path: Path, stack: ProjectStack):
        """Анализ package.json для определения менеджера пакетов и фреймворков."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            # Определение менеджера пакетов
            if (file_path.parent / 'yarn.lock').exists():
                stack.package_manager = 'yarn'
            elif (file_path.parent / 'pnpm-lock.yaml').exists():
                stack.package_manager = 'pnpm'
            elif (file_path.parent / 'package-lock.json').exists():
                stack.package_manager = 'npm'
            else:
                stack.package_manager = 'npm'  # по умолчанию

            # Определение фреймворков из зависимостей
            dependencies = {**package_data.get('dependencies', {}),
                            **package_data.get('devDependencies', {})}

            framework_mappings = {
                'react': 'react',
                'vue': 'vue',
                '@angular/core': 'angular',
                'svelte': 'svelte',
                'ember-source': 'ember',
                'backbone': 'backbone',
                'next': 'nextjs',
                'nuxt': 'nuxt',
                'gatsby': 'gatsby',
                'express': 'express',
                'koa': 'koa',
                '@nestjs/core': 'nest',
                'adonis': 'adonis',
                'sails': 'sails',
                'meteor': 'meteor',
                'electron': 'electron',
                'react-native': 'react-native',
                'ionic': 'ionic',
                '@capacitor/core': 'capacitor',
            }

            for dep, framework in framework_mappings.items():
                if dep in dependencies:
                    if framework not in stack.frameworks:
                        stack.frameworks.append(framework)

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Не удалось проанализировать package.json: {e}")

    def _add_language(self, language: str, stack: ProjectStack):
        """Добавление языка в список, если его еще нет."""
        if language not in stack.languages:
            stack.languages.append(language)

