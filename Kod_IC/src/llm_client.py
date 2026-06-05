import requests
import json
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    from .config import LM_STUDIO_URL, LM_MODEL
except ImportError:
    from config import LM_STUDIO_URL, LM_MODEL


class LLMClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or LM_STUDIO_URL
        self.model = model or LM_MODEL or "local-model"
        self.api_url = f"{self.base_url}/v1/chat/completions"

    def ask(self, prompt: str, system_prompt: str = None, temperature: float = 0.3) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }

        try:
            logger.info(f"Запрос к LLM: модель={self.model}")
            response = requests.post(self.api_url, json=payload, timeout=180)

            if response.status_code == 400:
                logger.error(f"LM Studio вернул 400 Bad Request. Детали: {response.text}")

            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"Не удалось подключиться к LM Studio на {self.base_url}")
        except Exception as e:
            raise RuntimeError(f"Ошибка LLM: {e}")

    def ask_json(self, prompt: str, system_prompt: str = None) -> dict:
        json_instruction = (
            "Ты строгий JSON-генератор. Отвечай ТОЛЬКО валидным JSON объектом или массивом. "
            "Никакого текста, никаких markdown-оберток, никаких пояснений. "
            "Начни ответ сразу с { или [."
        )

        if system_prompt:
            system_prompt = f"{system_prompt}\n{json_instruction}"
        else:
            system_prompt = json_instruction

        response_text = self.ask(prompt, system_prompt, temperature=0.1)
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Ответ LLM для парсинга: {response_text[:500]}")
            raise RuntimeError(f"LLM вернул не JSON: {e}")

    def check_connection(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code in [200, 404]
        except:
            return False


if __name__ == "__main__":
    client = LLMClient()
    print("Проверка подключения...")
    if client.check_connection():
        print("LM Studio доступен")
        print("Тестовый запрос...")
        print(client.ask("Напиши одним словом: ок"))
    else:
        print("LM Studio не доступен. Запусти сервер в приложении.")