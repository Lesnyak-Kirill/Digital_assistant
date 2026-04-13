try:
    from ..llm_client import LLMClient
    from ..prompts import load_prompt
except ImportError:
    from llm_client import LLMClient
    from prompts import load_prompt


def mark_roles(transcript: str) -> dict:
    """
    Определяет роли участников встречи.
    """
    client = LLMClient()
    prompt_template = load_prompt("roles")
    prompt = prompt_template.replace("{transcript}", transcript[:15000])

    print("[INFO] Распределение ролей...")
    roles_data = client.ask_json(prompt)

    return roles_data


if __name__ == "__main__":
    test_text = "Иванов: Давайте начнём. Петров: Я согласен. Сидоров: Нужно уточнить детали."
    result = mark_roles(test_text)
    print(result)