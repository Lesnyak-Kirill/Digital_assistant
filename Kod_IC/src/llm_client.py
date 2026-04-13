import requests
import json
from typing import Optional

try:
    from .config import LM_STUDIO_URL, LM_MODEL
except ImportError:
    from config import LM_STUDIO_URL, LM_MODEL


class LLMClient:
    """
    Клиент для работы с LM Studio (локальная LLM).
    """

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or LM_STUDIO_URL
        self.model = model or LM_MODEL
        self.api_url = f"{self.base_url}/v1/chat/completions"

    def ask(self, prompt: str, system_prompt: str = None, temperature: float = 0.3) -> str:
        """
        Отправляет запрос к LLM и возвращает ответ.
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Не удалось подключиться к LM Studio.\n"
                f"Проверь что сервер запущен на {self.base_url}\n"
                "В LM Studio: Server → Start Server"
            )
        except Exception as e:
            raise RuntimeError(f"Ошибка LLM: {e}")

    def ask_json(self, prompt: str, system_prompt: str = None) -> dict:
        """
        Отправляет запрос и ожидает JSON в ответе.
        """
        if not system_prompt:
            system_prompt = "Отвечай ТОЛЬКО валидным JSON без markdown и пояснений."
        else:
            system_prompt += "\nОтвечай ТОЛЬКО валидным JSON без markdown."

        response_text = self.ask(prompt, system_prompt, temperature=0.1)

        # Чистим ответ от markdown
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"LLM вернул не JSON: {e}\nОтвет: {response_text[:500]}")

    def check_connection(self) -> bool:
        """
        Проверяет доступность LM Studio.
        """
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False


#Тест подключения
if __name__ == "__main__":
    client = LLMClient()

    print("Проверка подключения к LM Studio...")
    if client.check_connection():
        print("- LM Studio доступен")

        # Тестовый запрос
        response = client.ask("Напиши одним предложением что ты умеешь")
        print(f"\nОтвет модели: {response}")
    else:
        print("LM Studio не доступен")
        print("Запусти LM Studio и включи сервер (Server → Start Server)")