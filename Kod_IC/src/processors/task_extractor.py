import json
from datetime import datetime

try:
    from ..llm_client import LLMClient
    from ..prompts import load_prompt
except ImportError:
    from llm_client import LLMClient
    from prompts import load_prompt


def extract_tasks(transcript: str) -> dict:
    """
    Извлекает задачи из транскрибата.
    Возвращает словарь с списком задач.
    """
    client = LLMClient()
    prompt_template = load_prompt("tasks")
    prompt = prompt_template.replace("{transcript}", transcript[:15000])

    print("[INFO] Извлечение задач...")
    tasks_data = client.ask_json(prompt)

    # Добавляем метаданные
    tasks_data["created_at"] = datetime.now().isoformat()
    tasks_data["total_tasks"] = len(tasks_data.get("tasks", []))

    return tasks_data


def save_tasks(tasks_data: dict, output_path: str):
    """
    Сохраняет задачи в JSON файл.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tasks_data, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Задачи сохранены: {output_path}")


if __name__ == "__main__":
    test_text = "Иванов сказал что нужно подготовить отчёт до пятницы. Петров возьмёт на себя презентацию."
    result = extract_tasks(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))