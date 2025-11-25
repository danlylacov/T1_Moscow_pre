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
        'typescript': [
            (r'app\.listen\(', 'express', 0.9),
            (r'express\(\)', 'express', 0.7),
            (r'module\.exports\s*=', 'node', 0.8),
            (r'export default', 'es6', 0.7),
            (r'require\([\'"]express[\'"]\)', 'express', 0.6),
            (r'import.*express', 'express', 0.6),
            (r'ReactDOM\.render\(', 'react', 0.9),
            (r'createApp\(', 'vue', 0.9),
            (r'bootstrapApplication\(', 'angular', 0.9),
            (r'@nestjs', 'nestjs', 0.8),
            (r'from [\'"]next[\'"]', 'nextjs', 0.8),
        ],
        'java': [
            (r'public static void main\(String\[\] args\)', 'java', 1.0),
            (r'fun main\(', 'kotlin', 1.0),  # Kotlin main function
            (r'@SpringBootApplication', 'spring-boot', 0.9),
            (r'SpringApplication\.run\(', 'spring-boot', 0.9),
            (r'@RestController', 'spring', 0.7),
            (r'io\.quarkus', 'quarkus', 0.8),
            (r'io\.micronaut', 'micronaut', 0.8),
            (r'io\.vertx', 'vertx', 0.8),
        ],
        'go': [
            (r'func main\(\)', 'go', 1.0),
            (r'package main', 'go', 0.8),
            (r'gin\.', 'gin', 0.7),
            (r'echo\.', 'echo', 0.7),
            (r'fiber\.', 'fiber', 0.7),
            (r'beego\.', 'beego', 0.7),
        ],
    }

    # Стандартные имена файлов точек входа
    STANDARD_ENTRY_FILES = {
        'python': ['main.py', 'app.py', 'application.py', 'run.py', 'wsgi.py', 'asgi.py', 'manage.py'],
        'typescript': ['index.ts', 'app.ts', 'server.ts', 'main.ts', 'src/index.ts', 'src/app.ts'],
        'java': ['Main.java', 'Application.java', 'src/main/java/**/*.java', 'Main.kt', 'Application.kt'],
        'go': ['main.go', 'cmd/**/*.go'],
    }

    # Расширенные паттерны для определения фреймворков
    FRAMEWORK_PATTERNS = {
        # Python фреймворки
        'django': [r'from django', r'import django', r'django\.', r'DJANGO_SETTINGS'],
        # Более строгие паттерны для Flask, чтобы избежать ложных срабатываний
        # Проверяем только реальные импорты и использование Flask
        'flask': [r'from flask import', r'from flask\.', r'import flask', r'\bFlask\(\)', r'@app\.route'],
        'fastapi': [r'from fastapi', r'import fastapi', r'fastapi\.', r'FastAPI\(\)'],

        # Java/Kotlin фреймворки
        # Spring (общий) - только общие паттерны Spring Framework, без Spring Boot
        # Обычно используется только если нет Spring Boot
        'spring': [r'org\.springframework\.(web|mvc|context|beans)', r'@SpringMvcTest', r'@SpringTest', r'@Controller', r'@Service'],
        # Spring Boot - специфичные паттерны (имеет приоритет над spring)
        'spring-boot': [r'@SpringBootApplication', r'SpringBootApplication', r'org\.springframework\.boot'],
        # Quarkus - только специфичные паттерны
        'quarkus': [r'io\.quarkus', r'@QuarkusTest', r'@QuarkusApplication', r'quarkus\.'],
        'micronaut': [r'io\.micronaut', r'@MicronautTest'],
        'vertx': [r'io\.vertx', r'Vertx'],

        # TypeScript/JavaScript фреймворки (Backend)
        'express': [r'require\([\'"]express[\'"]\)', r'import express', r'const express', r'from [\'"]express[\'"]'],
        'nest': [r'@nestjs/', r'import.*from [\'"]@nestjs/'],

        # TypeScript/JavaScript фреймворки (Frontend)
        'react': [r'require\([\'"]react[\'"]\)', r'import React', r'from [\'"]react[\'"]'],
        'vue': [r'require\([\'"]vue[\'"]\)', r'import Vue', r'from [\'"]vue[\'"]', r'createApp'],
        'angular': [r'@angular/', r'import.*from [\'"]@angular/'],
        'nextjs': [r'next/', r'import.*from [\'"]next[\'"]', r'getServerSideProps'],

        # Go фреймворки
        'gin': [r'github.com/gin-gonic/gin', r'gin\.'],
        'echo': [r'github.com/labstack/echo', r'echo\.'],
        'fiber': [r'github.com/gofiber/fiber', r'fiber\.'],
        'beego': [r'github.com/astaxie/beego', r'beego\.'],
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

    # Паттерны для баз данных (более строгие - ищем реальные импорты и использование)
    DATABASE_PATTERNS = {
        # PostgreSQL - ищем импорты и использование драйверов
        'postgresql': [r'import psycopg2', r'from psycopg2', r'require\([\'"]pg[\'"]\)', r'import.*pg[\'"]', r'pg\.connect', r'postgresql://'],
        # MySQL - ищем импорты драйверов
        'mysql': [r'import pymysql', r'import mysqldb', r'from pymysql', r'require\([\'"]mysql[\'"]\)', r'mysql\.createConnection', r'mysql://'],
        # MongoDB - ищем импорты драйверов
        'mongodb': [r'import pymongo', r'from pymongo', r'require\([\'"]mongodb[\'"]\)', r'require\([\'"]mongoose[\'"]\)', r'import.*mongoose', r'mongoose\.connect'],
        # Redis - ищем импорты драйверов
        'redis': [r'import redis', r'from redis', r'require\([\'"]redis[\'"]\)', r'redis\.createClient', r'redis\.NewClient'],
        # SQLite - ищем импорты
        'sqlite': [r'import sqlite3', r'from sqlite3', r'sqlite3\.connect', r'\.db[\'"]', r'\.sqlite[\'"]'],
        # Cassandra - ищем импорты
        'cassandra': [r'from cassandra', r'import cassandra', r'cassandra\.cluster'],
        # Elasticsearch - ищем импорты клиентов
        'elasticsearch': [r'from elasticsearch', r'import elasticsearch', r'Elasticsearch\(\)', r'require\([\'"]@elastic/elasticsearch[\'"]\)'],
        # Oracle - ищем импорты драйверов
        'oracle': [r'import cx_Oracle', r'from cx_Oracle', r'oracle\.connect'],
        # SQL Server - ищем импорты драйверов
        'sqlserver': [r'import pymssql', r'from pymssql', r'mssql://', r'sqlserver://'],
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
        'react', 'vue', 'angular', 'nextjs'
    }

    BACKEND_FRAMEWORKS = {
        'django', 'flask', 'fastapi',
        'spring', 'spring-boot', 'quarkus', 'micronaut', 'vertx',
        'express', 'nest',
        'gin', 'echo', 'fiber', 'beego'
    }

    MOBILE_FRAMEWORKS = set()  # Мобильные фреймворки не поддерживаются

