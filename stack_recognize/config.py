"""Конфигурация и паттерны для определения технологического стека."""
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


class ConfigLoader:
    """Загрузчик конфигурации из JSON файла и встроенных паттернов."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация загрузчика конфигурации.

        Args:
            config_path: Путь к JSON файлу конфигурации. Если None, используется detect_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent / "detect_config.json"

        self.config_path = Path(config_path)
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из JSON файла."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга конфигурационного файла: {e}")

    @property
    def languages(self) -> Dict[str, Any]:
        """Получить конфигурацию языков."""
        return self.config_data.get('languages', {})

    @property
    def frameworks(self) -> Dict[str, Any]:
        """Получить конфигурацию фреймворков."""
        return self.config_data.get('frameworks', {})

    @property
    def package_managers(self) -> Dict[str, Any]:
        """Получить конфигурацию менеджеров пакетов."""
        return self.config_data.get('package_managers', {})

    @property
    def test_runners(self) -> Dict[str, Any]:
        """Получить конфигурацию тестовых раннеров."""
        return self.config_data.get('test_runners', {})

    @property
    def cicd(self) -> Dict[str, Any]:
        """Получить конфигурацию CI/CD."""
        return self.config_data.get('cicd', {})

    @property
    def devops(self) -> Dict[str, Any]:
        """Получить конфигурацию DevOps инструментов."""
        return self.config_data.get('devops', {})


class PatternConfig:
    """Встроенные паттерны для определения технологий."""

    # Паттерны для определения точек входа
    ENTRY_POINT_PATTERNS = {
        'python': [
            (r'if __name__ == [\'"]__main__[\'"]', 'main', 0.9),
            (r'app\.run\(', 'flask', 0.8),
            (r'application\.run\(', 'flask', 0.8),
            (r'uvicorn\.run\(', 'fastapi', 0.9),
            (r'manage\.py', 'django', 1.0),
            (r'from django\.', 'django', 0.7),
            (r'Flask\(\)', 'flask', 0.6),
            (r'FastAPI\(\)', 'fastapi', 0.8),
        ],
        'javascript': [
            (r'app\.listen\(', 'express', 0.9),
            (r'express\(\)', 'express', 0.7),
            (r'module\.exports\s*=', 'node', 0.8),
            (r'export default', 'es6', 0.7),
            (r'require\([\'"]express[\'"]\)', 'express', 0.6),
            (r'ReactDOM\.render\(', 'react', 0.9),
            (r'createApp\(', 'vue', 0.9),
            (r'bootstrapApplication\(', 'angular', 0.9),
        ],
        'java': [
            (r'public static void main\(String\[\] args\)', 'java', 1.0),
            (r'@SpringBootApplication', 'spring', 0.9),
            (r'SpringApplication\.run\(', 'spring', 0.9),
            (r'@RestController', 'spring', 0.7),
        ],
        'php': [
            (r'<?php', 'php', 0.5),
            (r'laravel/framework', 'laravel', 0.8),
            (r'Illuminate\\', 'laravel', 0.7),
            (r'symfony/', 'symfony', 0.8),
        ],
        'ruby': [
            (r'Ruby on Rails', 'rails', 0.8),
            (r'require [\'"]rails[\'"]', 'rails', 0.7),
            (r'Rails\.application', 'rails', 0.9),
            (r'Sinatra::Application', 'sinatra', 0.9),
        ],
        'go': [
            (r'func main\(\)', 'go', 1.0),
            (r'package main', 'go', 0.8),
        ],
        'rust': [
            (r'fn main\(\)', 'rust', 1.0),
            (r'#\[tokio::main\]', 'tokio', 0.9),
        ]
    }

    # Стандартные имена файлов точек входа
    STANDARD_ENTRY_FILES = {
        'python': ['main.py', 'app.py', 'application.py', 'run.py', 'wsgi.py', 'asgi.py', 'manage.py'],
        'javascript': ['index.js', 'app.js', 'server.js', 'main.js', 'src/index.js', 'src/app.js'],
        'typescript': ['index.ts', 'app.ts', 'server.ts', 'main.ts', 'src/index.ts', 'src/app.ts'],
        'java': ['Main.java', 'Application.java', 'src/main/java/**/*.java'],
        'php': ['index.php', 'app.php', 'server.php', 'public/index.php'],
        'ruby': ['app.rb', 'application.rb', 'config.ru', 'bin/rails'],
        'go': ['main.go', 'cmd/**/*.go'],
        'rust': ['main.rs', 'src/main.rs'],
        'csharp': ['Program.cs', 'Startup.cs'],
        'html': ['index.html', 'default.html', 'public/index.html'],
    }

    # Расширенные паттерны для определения фреймворков
    FRAMEWORK_PATTERNS = {
        # Python фреймворки
        'django': [r'from django', r'import django', r'django\.', r'DJANGO_SETTINGS'],
        'flask': [r'from flask', r'import flask', r'flask\.', r'Flask\(\)'],
        'fastapi': [r'from fastapi', r'import fastapi', r'fastapi\.', r'FastAPI\(\)'],
        'sanic': [r'from sanic', r'import sanic', r'sanic\.'],
        'tornado': [r'import tornado', r'tornado\.'],
        'bottle': [r'import bottle', r'bottle\.'],
        'cherrypy': [r'import cherrypy', r'cherrypy\.'],

        # Java фреймворки
        'spring': [r'org\.springframework', r'@SpringBootApplication', r'SpringApplication'],
        'spring-boot': [r'@SpringBootApplication', r'SpringBootApplication'],
        'jakarta-ee': [r'jakarta\.', r'javax\.enterprise'],
        'quarkus': [r'io\.quarkus', r'@QuarkusTest'],
        'micronaut': [r'io\.micronaut', r'@MicronautTest'],
        'vertx': [r'io\.vertx', r'Vertx'],
        'play': [r'play\.', r'import play\.'],

        # JavaScript/TypeScript фреймворки
        'express': [r'require\([\'"]express[\'"]\)', r'import express', r'const express'],
        'koa': [r'require\([\'"]koa[\'"]\)', r'import koa', r'const Koa'],
        'nest': [r'@nestjs/', r'import.*from [\'"]@nestjs/'],
        'adonis': [r'@adonisjs/', r'adonis'],
        'sails': [r'sails', r'require\([\'"]sails[\'"]\)'],
        'meteor': [r'meteor/', r'Package\.use'],

        # Frontend фреймворки
        'react': [r'require\([\'"]react[\'"]\)', r'import React', r'from [\'"]react[\'"]'],
        'vue': [r'require\([\'"]vue[\'"]\)', r'import Vue', r'from [\'"]vue[\'"]'],
        'angular': [r'@angular/', r'import.*from [\'"]@angular/'],
        'svelte': [r'svelte', r'import.*from [\'"]svelte[\'"]'],
        'ember': [r'ember', r'import Ember'],
        'backbone': [r'backbone', r'import Backbone'],
        'nextjs': [r'next/', r'import.*from [\'"]next[\'"]'],
        'nuxt': [r'nuxt/', r'import.*from [\'"]nuxt[\'"]'],
        'gatsby': [r'gatsby', r'import.*from [\'"]gatsby[\'"]'],

        # PHP фреймворки
        'laravel': [r'Illuminate\\', r'use Illuminate\\', r'laravel/framework'],
        'symfony': [r'use Symfony\\', r'Symfony\\\\', r'namespace Symfony'],
        'codeigniter': [r'CI_', r'use CodeIgniter'],
        'yii': [r'Yii::', r'namespace yii\\'],
        'cakephp': [r'Cake\\', r'use Cake\\'],
        'zend': [r'Zend_', r'Laminas'],

        # Ruby фреймворки
        'rails': [r'require [\'"]rails[\'"]', r'Rails\.', r'ActiveRecord'],
        'sinatra': [r'require [\'"]sinatra[\'"]', r'Sinatra::'],
        'hanami': [r'Hanami::', r'require [\'"]hanami[\'"]'],

        # Go фреймворки
        'gin': [r'github.com/gin-gonic/gin', r'gin\.'],
        'echo': [r'github.com/labstack/echo', r'echo\.'],
        'fiber': [r'github.com/gofiber/fiber', r'fiber\.'],
        'beego': [r'github.com/astaxie/beego', r'beego\.'],

        # Rust фреймворки
        'actix': [r'actix_web', r'use actix_web'],
        'rocket': [r'rocket', r'#\[rocket::'],
        'warp': [r'warp', r'use warp'],

        # .NET фреймворки
        'aspnet-core': [r'Microsoft\.AspNetCore', r'using Microsoft\.AspNetCore'],
        'aspnet-mvc': [r'System\.Web\.Mvc', r'using System\.Web\.Mvc'],
        'blazor': [r'Microsoft\.AspnetCore\.Components', r'Blazor'],

        # Mobile фреймворки
        'react-native': [r'react-native', r'import.*from [\'"]react-native[\'"]'],
        'flutter': [r'flutter/', r'import.*flutter'],
        'ionic': [r'ionic', r'import.*ionic'],
        'cordova': [r'cordova', r'org\.apache\.cordova'],
        'capacitor': [r'@capacitor/', r'import.*from [\'"]@capacitor/'],

        # Другие
        'electron': [r'electron', r'require\([\'"]electron[\'"]\)'],
    }

    # Паттерны для тестовых раннеров
    TEST_RUNNER_PATTERNS = {
        'pytest': [r'import pytest', r'pytest\.', r'@pytest\.'],
        'unittest': [r'import unittest', r'unittest\.'],
        'jest': [r'jest\.config\.', r'jest[\'"]', r'describe\(', r'it\('],
        'mocha': [r'mocha[\'"]', r'describe\(', r'it\(', r'beforeEach\('],
        'jasmine': [r'jasmine', r'describe\(', r'it\('],
        'karma': [r'karma', r'karma\.config\.'],
        'cypress': [r'cypress', r'cy\.'],
        'playwright': [r'playwright', r'page\.'],
        'phpunit': [r'PHPUnit\\\\', r'use PHPUnit\\\\', r'@test'],
        'junit': [r'junit', r'@Test', r'org\.junit'],
        'testng': [r'TestNG', r'org\.testng'],
        'rspec': [r'require [\'"]rspec[\'"]', r'RSpec\.', r'describe '],
        'cucumber': [r'cucumber', r'Given\(', r'When\(', r'Then\('],
        'selenium': [r'selenium', r'webdriver'],
    }

    # Паттерны для баз данных
    DATABASE_PATTERNS = {
        'postgresql': [r'postgresql', r'postgres', r'pg\.', r'psycopg2'],
        'mysql': [r'mysql', r'mysqldb', r'pymysql'],
        'mongodb': [r'mongodb', r'pymongo', r'mongoose'],
        'redis': [r'redis', r'redis-py'],
        'sqlite': [r'sqlite', r'sqlite3'],
        'cassandra': [r'cassandra', r'cql'],
        'elasticsearch': [r'elasticsearch', r'elastic'],
        'oracle': [r'oracle', r'cx_oracle'],
        'sqlserver': [r'sqlserver', r'pymssql', r'microsoft\.sql'],
    }

    # Паттерны для облачных платформ
    CLOUD_PATTERNS = {
        'aws': [r'aws', r'boto3', r'aws-sdk'],
        'azure': [r'azure', r'azure-sdk'],
        'gcp': [r'google\.cloud', r'gcp', r'google-cloud'],
        'digitalocean': [r'digitalocean', r'do-spaces'],
        'heroku': [r'heroku', r'Procfile'],
    }

    # Классификация фреймворков
    FRONTEND_FRAMEWORKS = {
        'react', 'vue', 'angular', 'svelte', 'ember', 'backbone',
        'nextjs', 'nuxt', 'gatsby'
    }

    BACKEND_FRAMEWORKS = {
        'django', 'flask', 'fastapi', 'sanic', 'tornado', 'bottle', 'cherrypy',
        'spring', 'spring-boot', 'jakarta-ee', 'quarkus', 'micronaut', 'vertx', 'play',
        'express', 'koa', 'nest', 'adonis', 'sails', 'meteor',
        'laravel', 'symfony', 'codeigniter', 'yii', 'cakephp', 'zend',
        'rails', 'sinatra', 'hanami',
        'gin', 'echo', 'fiber', 'beego',
        'actix', 'rocket', 'warp',
        'aspnet-core', 'aspnet-mvc', 'blazor'
    }

    MOBILE_FRAMEWORKS = {
        'react-native', 'flutter', 'ionic', 'cordova', 'capacitor'
    }

