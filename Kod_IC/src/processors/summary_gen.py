try:
    from ..llm_client import LLMClient
    from ..prompts import load_prompt
except ImportError:
    from llm_client import LLMClient
    from prompts import load_prompt


def generate_summary(transcript: str) -> str:
    """
    Генерирует саммари встречи по транскрибату.
    """
    client = LLMClient()
    prompt_template = load_prompt("summary")
    prompt = prompt_template.replace("{transcript}", transcript[:15000])  # лимит токенов

    print("[INFO] Генерация саммари...")
    summary = client.ask(prompt)

    return summary


if __name__ == "__main__":
    # Тест
    test_text = "Обсуждали бюджет проекта. Решили увеличить на 10%. Срок до конца квартала."
    result = generate_summary(test_text)
    print(result)