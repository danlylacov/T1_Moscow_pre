from langchain_openai import ChatOpenAI
import json


def generate_cicd_pipeline_simple(project_data, api_key):
    """Упрощенная версия без использования агента"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.1, openai_api_key=api_key)

    prompt = f"""
    Ты - эксперт по CI/CD. Сгенерируй GitLab CI пайплайн на основе этого стека:

    {json.dumps(project_data, indent=2)}

    Требования:
    - Stages: {project_data['user_settings']['stages']}
    - Python версия: {project_data['user_settings']['variables']['PYTHON_VERSION']}
    - Основной файл: {project_data['analysis']['main_entry']['path']}
    - Docker: {project_data['analysis']['docker']}
    - Тесты: {project_data['analysis']['test_runner']}

    Добавь:
    1. Кэширование pip пакетов
    2. Сканирование безопасности (trivy/bandit)
    3. Сборку Docker образа если docker=true
    4. Триггеры по веткам и MR

    Верни ТОЛЬКО YAML код без комментариев.
    """

    response = llm.invoke(prompt)
    return response.content


# Использование
api_key = "your-api-key"
project_data = {...}  # ваш JSON

pipeline = generate_cicd_pipeline_simple(project_data, api_key)
print(pipeline)