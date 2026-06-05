import os
from pathlib import Path
from dotenv import load_dotenv

#Загружаем .env
load_dotenv()

#Базовая директория (где лежит этот файл)
BASE_DIR = Path(__file__).resolve().parent.parent

#Пути к папкам
INPUT_DIR = BASE_DIR / os.getenv("INPUT_PATH", "data/input")
OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_PATH", "data/output")
TMP_DIR = BASE_DIR / os.getenv("TMP_PATH", "data/tmp")

#Модель Vosk
MODEL_DIR = BASE_DIR / os.getenv("MODEL_PATH", "models/vosk-ru")

#Создаём папки если их нет
for d in [INPUT_DIR, OUTPUT_DIR, TMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

#LM Studio
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234")
LM_MODEL = os.getenv("LM_MODEL", "meta-llama-3.1-8b-instruct")

#Vosk настройки
VOSK_SAMPLE_RATE = int(os.getenv("VOSK_SAMPLE_RATE", "16000"))
VOSK_CHUNK_SIZE = int(os.getenv("VOSK_CHUNK_SIZE", "4000"))

#Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / os.getenv("LOG_FILE", "logs/app.log")