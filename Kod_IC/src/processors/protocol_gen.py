try:
    from ..llm_client import LLMClient
    from ..prompts import load_prompt
except ImportError:
    from llm_client import LLMClient
    from prompts import load_prompt


def generate_protocol(transcript: str, participants: list = None) -> str:
    """
    Генерирует официальный протокол встречи.
    """
    client = LLMClient()
    prompt_template = load_prompt("protocol")

    context = ""
    if participants:
        context = f"Участники: {', '.join(participants)}\n\n"

    prompt = prompt_template.replace("{transcript}", context + transcript[:15000])

    print("[INFO] Генерация протокола...")
    protocol = client.ask(prompt)

    return protocol


if __name__ == "__main__":
    test_text = "Иванов предложил увеличить бюджет. Петров поддержал. Решили голосовать."
    result = generate_protocol(test_text)
    print(result)