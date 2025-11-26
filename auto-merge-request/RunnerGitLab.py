import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from GitLabRepoService import GitLabRepoService
except ImportError:
    print("Ошибка: файл GitLabRepoService не найден в текущей директории.")
    logger.error("Ошибка: файл gitlab_service.py не найден в текущей директории.")


def string_to_yaml_file(yaml_content: str, file_name: str):
    """
    Сохраняет текстовую строку в файл .yml
    """
    try:
        # Используем utf-8 для корректной записи кириллицы и спецсимволов
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(yaml_content.strip())  # .strip() убирает лишние пробелы в начале/конце

        print(f"✅ Файл успешно создан: {os.path.abspath(file_name)}")

    except Exception as e:
        print(f"❌ Ошибка при записи файла: {e}")

##!!!! Важно метод считывает файл из корня если надо по другому то {Использовать метод string_to_yaml_file}
def run_process(repo_link, repo_token, branch, file_name_on_disk):
    # 1. Конфигурация
    # Ссылка на репозиторий (куда будем делать MR)
    # repo_link = "https://gitlab.com/viktorgezz/git-service-1"

    # Токен доступа (лучше брать из переменных окружения для безопасности)
    # export GITLAB_TOKEN=your_token_here
    # repo_token = os.getenv("GITLAB_TOKEN")
    # Базовая ветка в оригинальном репозитории (обычно main или master)
    # base_branch = "main"

    # 2. Подготовка файла (эмуляция чтения байтов)
    # Пытаемся прочитать реальный файл,
    # file_name_on_disk = "pipeline.yml"

    if os.path.exists(file_name_on_disk):
        print(f"Чтение файла: {file_name_on_disk}")
        with open(file_name_on_disk, "rb") as f:
            file_bytes = f.read()
    else:
        logger.error(f"file {file_name_on_disk} not found")

    # 3. Инициализация и запуск сервиса
    runner = GitLabRepoService()

    logger.info(f"Запуск процесса для репозитория: {repo_link}")

    try:
        runner.modify_repo(
            link=repo_link,
            token=repo_token,
            base_branch=branch,
            file_content=file_bytes
        )
        logger.info("Готово! Процесс завершен успешно.")

    except Exception as e:
        logger.error(f"Произошла ошибка при выполнении: {e}")
