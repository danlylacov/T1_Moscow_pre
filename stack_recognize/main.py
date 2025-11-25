"""Точка входа для анализа технологического стека проекта."""
import json

try:
    from .detector import ProjectStackDetector
except ImportError:
    from detector import ProjectStackDetector


def main():
    """Основная функция для запуска анализа."""
    detector = ProjectStackDetector()

    # Пример с тестовым репозиторием (замените на реальный URL)
    repo_url = "https://github.com/danlylacov/VolumeHub"

    try:
        stack = detector.detect_stack(repo_url)
        print("Обнаруженный стек технологий:")
        print(f"Языки: {stack.languages}")
        print(f"Фреймворки: {stack.frameworks}")
        print(f"Frontend фреймворки: {stack.frontend_frameworks}")
        print(f"Backend фреймворки: {stack.backend_frameworks}")
        print(f"Mobile фреймворки: {stack.mobile_frameworks}")
        print(f"Менеджер пакетов: {stack.package_manager}")
        print(f"Тестовые раннеры: {stack.test_runner}")
        print(f"Docker: {stack.docker}")
        print(f"Kubernetes: {stack.kubernetes}")
        print(f"Terraform: {stack.terraform}")
        print(f"CI/CD: {stack.cicd}")
        print(f"Базы данных: {stack.databases}")
        print(f"Облачные платформы: {stack.cloud_platforms}")
        print(f"Инструменты сборки: {stack.build_tools}")
        print(f"Подсказки: {stack.hints}")

        print("\nТочки входа:")
        for i, entry in enumerate(stack.entry_points, 1):
            print(f"{i}. {entry.file_path} ({entry.type}, {entry.language}, уверенность: {entry.confidence})")

        if stack.main_entry_point:
            print(f"\nОсновная точка входа: {stack.main_entry_point.file_path}")
            print(f"Тип: {stack.main_entry_point.type}, Язык: {stack.main_entry_point.language}")
            print(f"Фреймворк: {stack.main_entry_point.framework}")
            print(f"Уверенность: {stack.main_entry_point.confidence}")

        #print(f"\nОбнаруженные файлы: {json.dumps(stack.files_detected, indent=2, ensure_ascii=False)}")

    except Exception as e:
        print(f"Ошибка при анализе репозитория: {e}")


if __name__ == "__main__":
    main()
