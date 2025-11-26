"""CLI интерфейс для Self-Deploy Core Service."""
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

import click

from app import storage
from app.database import Base, engine, get_db
from app.schemas import Project, ProjectCreate, PipelineGenerationCreate
from app.services.analyzer import analyze_repository, get_full_stack
from app.services.pipeline_generator import generate_pipeline


def init_db():
    """Инициализировать базу данных."""
    Base.metadata.create_all(bind=engine)


@click.group()
def cli():
    """Self-Deploy CLI - управление проектами и генерация CI/CD пайплайнов."""
    pass


@cli.command()
@click.option("--name", required=True, help="Название проекта")
@click.option("--url", required=True, help="URL Git-репозитория")
@click.option("--token", default="", help="Токен для клонирования репозитория")
def add_project(name: str, url: str, token: str):
    """Добавить новый проект и проанализировать его стек."""
    click.echo(f"Анализ репозитория {url}...")
    
    try:
        # Анализ репозитория
        analysis = analyze_repository(url, token)
        
        # Создание проекта
        project_create = ProjectCreate(
            name=name,
            url=url,
            clone_token=token,
            analysis=analysis
        )
        
        db = next(get_db())
        project = storage.create_project(db, project_create)
        
        click.echo(f"✓ Проект '{project.name}' успешно добавлен (ID: {project.id})")
        click.echo(f"  Языки: {', '.join(analysis.languages) if analysis.languages else 'не определены'}")
        click.echo(f"  Фреймворки: {', '.join(analysis.frameworks) if analysis.frameworks else 'не определены'}")
        click.echo(f"  Docker: {'да' if analysis.docker else 'нет'}")
        
    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        sys.exit(1)


@cli.command()
def list_projects():
    """Показать список всех проектов."""
    db = next(get_db())
    projects = storage.list_projects(db)
    
    if not projects:
        click.echo("Проекты не найдены.")
        return
    
    click.echo(f"Найдено проектов: {len(projects)}\n")
    for project in projects:
        click.echo(f"ID: {project.id}")
        click.echo(f"  Название: {project.name}")
        click.echo(f"  URL: {project.url}")
        if project.analysis:
            click.echo(f"  Языки: {', '.join(project.analysis.languages) if project.analysis.languages else 'не определены'}")
        click.echo()


@cli.command()
@click.option("--project-id", type=int, required=True, help="ID проекта")
@click.option("--output", type=click.Path(), help="Путь для сохранения пайплайна (опционально)")
@click.option("--platform", default="gitlab", help="Платформа CI/CD (gitlab/jenkins)")
@click.option("--stages", help="Список стадий через запятую (опционально)")
def generate(project_id: int, output: Optional[str], platform: str, stages: Optional[str]):
    """Сгенерировать CI/CD пайплайн для проекта."""
    db = next(get_db())
    project = storage.get_project(db, project_id)
    
    if not project:
        click.echo(f"✗ Проект с ID {project_id} не найден", err=True)
        sys.exit(1)
    
    if not project.analysis:
        click.echo(f"✗ Для проекта {project_id} отсутствует анализ. Сначала выполните анализ.", err=True)
        sys.exit(1)
    
    click.echo(f"Генерация пайплайна для проекта '{project.name}'...")
    
    try:
        # Настройки генерации
        user_settings: Dict[str, Any] = {
            "platform": platform,
            "stages": stages.split(",") if stages else [],
            "triggers": {
                "on_push": ["main", "master"],
                "on_merge_request": False,
                "on_tags": "",
                "schedule": "",
                "manual": False,
            },
            "variables": {},
        }
        
        # Генерация пайплайна
        pipeline = generate_pipeline(project.analysis, user_settings)
        
        # Сохранение в БД
        create_dto = PipelineGenerationCreate(
            project_id=project_id,
            uml=pipeline,
        )
        generation = storage.create_pipeline_generation(db, create_dto)
        
        # Вывод или сохранение
        if output:
            Path(output).write_text(pipeline, encoding="utf-8")
            click.echo(f"✓ Пайплайн сохранен в {output}")
        else:
            click.echo("\n" + "="*80)
            click.echo(pipeline)
            click.echo("="*80)
        
        click.echo(f"✓ Пайплайн сгенерирован (ID генерации: {generation.id})")
        
    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option("--url", required=True, help="URL Git-репозитория")
@click.option("--token", default="", help="Токен для клонирования репозитория")
@click.option("--output", type=click.Path(), help="Путь для сохранения пайплайна")
@click.option("--platform", default="gitlab", help="Платформа CI/CD (gitlab/jenkins)")
@click.option("--stack-output", type=click.Path(), help="Путь для сохранения стека проекта (JSON)")
def generate_from_repo(url: str, token: str, output: Optional[str], platform: str, stack_output: Optional[str]):
    """Сгенерировать CI/CD пайплайн напрямую из репозитория со всеми возможными стадиями."""
    click.echo(f"Анализ репозитория {url}...")
    
    try:
        # Получаем полный стек для сохранения
        full_stack = get_full_stack(url, token)
        
        # Анализ репозитория
        analysis = analyze_repository(url, token)
        
        # Сохраняем стек в файл, если указан
        if stack_output:
            import json
            # Извлекаем docker пути - все Dockerfile
            docker_context = None
            dockerfile_path = None
            dockerfile_paths = []
            
            docker_all = full_stack.files_detected.get("docker_all") if hasattr(full_stack, "files_detected") else None
            docker_files = full_stack.files_detected.get("docker") if hasattr(full_stack, "files_detected") else None
            
            if docker_all:
                if isinstance(docker_all, list):
                    dockerfile_paths = docker_all
                elif isinstance(docker_all, str):
                    dockerfile_paths = [docker_all]
            elif docker_files:
                if isinstance(docker_files, list):
                    dockerfile_paths = docker_files
                elif isinstance(docker_files, str):
                    dockerfile_paths = [docker_files]
            
            # Убираем дубликаты
            seen = set()
            unique_paths = []
            for path in dockerfile_paths:
                if path not in seen:
                    seen.add(path)
                    unique_paths.append(path)
            dockerfile_paths = unique_paths
            
            if dockerfile_paths:
                dockerfile_path = dockerfile_paths[0]
                from pathlib import Path as PathLib
                context_path = str(PathLib(dockerfile_path).parent)
                docker_context = context_path if context_path != "." else ""
            
            stack_info = {
                "languages": full_stack.languages,
                "frameworks": full_stack.frameworks,
                "frontend_frameworks": full_stack.frontend_frameworks,
                "backend_frameworks": full_stack.backend_frameworks,
                "package_manager": full_stack.package_manager,
                "test_runner": full_stack.test_runner,
                "docker": full_stack.docker,
                "docker_context": docker_context,
                "dockerfile_path": dockerfile_path,
                "dockerfile_paths": dockerfile_paths,
                "kubernetes": full_stack.kubernetes,
                "terraform": full_stack.terraform,
                "databases": full_stack.databases,
                "cloud_platforms": full_stack.cloud_platforms,
                "build_tools": full_stack.build_tools,
                "cicd": full_stack.cicd,
            }
            Path(stack_output).write_text(json.dumps(stack_info, indent=2, ensure_ascii=False), encoding="utf-8")
            click.echo(f"✓ Стек проекта сохранен в {stack_output}")
        
        # Настройки со всеми стадиями
        user_settings: Dict[str, Any] = {
            "platform": platform,
            "stages": [
                "pre_checks", "lint", "type_check", "security", "test",
                "build", "docker_build", "docker_push", "integration",
                "migration", "deploy", "post_deploy", "cleanup"
            ],
            "triggers": {
                "on_push": ["main", "master"],
                "on_merge_request": False,
                "on_tags": "",
                "schedule": "",
                "manual": False,
            },
            "variables": {},
            "docker_registry": "$CI_REGISTRY",
            "docker_image": "$CI_REGISTRY_IMAGE",
            "docker_context": analysis.docker_context if analysis.docker else ".",
            "dockerfile_path": analysis.dockerfile_path if analysis.docker else "Dockerfile",
        }
        
        # Генерация пайплайна
        pipeline = generate_pipeline(analysis, user_settings)
        
        # Сохранение или вывод
        if output:
            Path(output).write_text(pipeline, encoding="utf-8")
            click.echo(f"✓ Пайплайн сохранен в {output}")
        else:
            click.echo("\n" + "="*80)
            click.echo(pipeline)
            click.echo("="*80)
        
        click.echo("✓ Пайплайн успешно сгенерирован")
        
    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option("--url", required=True, help="URL Git-репозитория")
@click.option("--token", default="", help="Токен для клонирования репозитория")
@click.option("--output", type=click.Path(), help="Путь для сохранения стека (JSON)")
def analyze_repo(url: str, token: str, output: Optional[str]):
    """Определить стек проекта и вывести его в консоль (или сохранить в файл)."""
    click.echo(f"Анализ репозитория {url}...")
    
    try:
        # Получаем полный стек
        stack = get_full_stack(url, token)
        
        # Формируем информацию о стеке
        # Извлекаем docker пути - все Dockerfile
        docker_context = None
        dockerfile_path = None
        dockerfile_paths = []
        
        docker_all = stack.files_detected.get("docker_all") if hasattr(stack, "files_detected") else None
        docker_files = stack.files_detected.get("docker") if hasattr(stack, "files_detected") else None
        
        if docker_all:
            if isinstance(docker_all, list):
                dockerfile_paths = docker_all
            elif isinstance(docker_all, str):
                dockerfile_paths = [docker_all]
        elif docker_files:
            if isinstance(docker_files, list):
                dockerfile_paths = docker_files
            elif isinstance(docker_files, str):
                dockerfile_paths = [docker_files]
        
        # Убираем дубликаты
        seen = set()
        unique_paths = []
        for path in dockerfile_paths:
            if path not in seen:
                seen.add(path)
                unique_paths.append(path)
        dockerfile_paths = unique_paths
        
        if dockerfile_paths:
            dockerfile_path = dockerfile_paths[0]
            from pathlib import Path as PathLib
            context_path = str(PathLib(dockerfile_path).parent)
            docker_context = context_path if context_path != "." else ""
        
        stack_info = {
            "languages": stack.languages,
            "frameworks": stack.frameworks,
            "frontend_frameworks": stack.frontend_frameworks,
            "backend_frameworks": stack.backend_frameworks,
            "package_manager": stack.package_manager,
            "test_runner": stack.test_runner,
            "docker": stack.docker,
            "docker_context": docker_context,
            "dockerfile_path": dockerfile_path,
            "dockerfile_paths": dockerfile_paths,
            "kubernetes": stack.kubernetes,
            "terraform": stack.terraform,
            "databases": stack.databases,
            "cloud_platforms": stack.cloud_platforms,
            "build_tools": stack.build_tools,
            "cicd": stack.cicd,
        }
        
        # Выводим в консоль
        click.echo("\n" + "="*80)
        click.echo("ТЕХНОЛОГИЧЕСКИЙ СТЕК ПРОЕКТА")
        click.echo("="*80)
        click.echo(f"Языки: {', '.join(stack.languages) if stack.languages else 'не определены'}")
        click.echo(f"Фреймворки: {', '.join(stack.frameworks) if stack.frameworks else 'не определены'}")
        click.echo(f"Frontend фреймворки: {', '.join(stack.frontend_frameworks) if stack.frontend_frameworks else 'не определены'}")
        click.echo(f"Backend фреймворки: {', '.join(stack.backend_frameworks) if stack.backend_frameworks else 'не определены'}")
        click.echo(f"Менеджер пакетов: {stack.package_manager or 'не определен'}")
        click.echo(f"Тестовые раннеры: {', '.join(stack.test_runner) if stack.test_runner else 'не определены'}")
        # Извлекаем docker пути для вывода - все Dockerfile
        dockerfile_paths = []
        docker_all = stack.files_detected.get("docker_all") if hasattr(stack, "files_detected") else None
        docker_files = stack.files_detected.get("docker") if hasattr(stack, "files_detected") else None
        
        if docker_all:
            if isinstance(docker_all, list):
                dockerfile_paths = docker_all
            elif isinstance(docker_all, str):
                dockerfile_paths = [docker_all]
        elif docker_files:
            if isinstance(docker_files, list):
                dockerfile_paths = docker_files
            elif isinstance(docker_files, str):
                dockerfile_paths = [docker_files]
        
        # Убираем дубликаты
        seen = set()
        unique_paths = []
        for path in dockerfile_paths:
            if path not in seen:
                seen.add(path)
                unique_paths.append(path)
        dockerfile_paths = unique_paths
        
        click.echo(f"Docker: {'да' if stack.docker else 'нет'}")
        if stack.docker and dockerfile_paths:
            if len(dockerfile_paths) == 1:
                dockerfile_path = dockerfile_paths[0]
                click.echo(f"  Dockerfile: {dockerfile_path}")
                from pathlib import Path as PathLib
                context_path = str(PathLib(dockerfile_path).parent)
                if context_path != ".":
                    click.echo(f"  Docker context: {context_path}")
            else:
                click.echo(f"  Dockerfile файлов: {len(dockerfile_paths)}")
                for i, df_path in enumerate(dockerfile_paths, 1):
                    from pathlib import Path as PathLib
                    context_path = str(PathLib(df_path).parent)
                    click.echo(f"    {i}. {df_path} (context: {context_path if context_path != '.' else 'root'})")
        click.echo(f"Kubernetes: {'да' if stack.kubernetes else 'нет'}")
        click.echo(f"Terraform: {'да' if stack.terraform else 'нет'}")
        click.echo(f"Базы данных: {', '.join(stack.databases) if stack.databases else 'не определены'}")
        click.echo(f"Облачные платформы: {', '.join(stack.cloud_platforms) if stack.cloud_platforms else 'не определены'}")
        click.echo(f"Инструменты сборки: {', '.join(stack.build_tools) if stack.build_tools else 'не определены'}")
        click.echo(f"CI/CD: {', '.join(stack.cicd) if stack.cicd else 'не определены'}")
        click.echo("="*80)
        
        # Сохраняем в файл, если указан
        if output:
            import json
            Path(output).write_text(json.dumps(stack_info, indent=2, ensure_ascii=False), encoding="utf-8")
            click.echo(f"✓ Стек сохранен в {output}")
        
        click.echo("✓ Анализ завершен")
        
    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
def list_pipelines():
    """Показать историю генерации пайплайнов."""
    db = next(get_db())
    pipelines = storage.list_pipeline_generations(db)
    
    if not pipelines:
        click.echo("История генераций пуста.")
        return
    
    click.echo(f"Найдено генераций: {len(pipelines)}\n")
    for pipeline in pipelines:
        click.echo(f"ID: {pipeline.id}")
        click.echo(f"  Проект ID: {pipeline.project_id or 'N/A'}")
        click.echo(f"  Создан: {pipeline.generated_at}")
        click.echo(f"  Размер пайплайна: {len(pipeline.uml)} символов")
        click.echo()


@cli.command()
def init():
    """Инициализировать базу данных."""
    click.echo("Инициализация базы данных...")
    init_db()
    click.echo("✓ База данных инициализирована")


if __name__ == "__main__":
    cli()

