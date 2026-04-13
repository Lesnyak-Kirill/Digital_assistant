from pathlib import Path

PROMPTS_DIR = Path(__file__).parent

def load_prompt(name: str) -> str:
    """Загружает текст промпта из файла."""
    file_path = PROMPTS_DIR / f"{name}.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()