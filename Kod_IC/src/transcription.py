import json
import os
import subprocess
from pathlib import Path

try:
    from .config import MODEL_DIR, TMP_DIR, VOSK_SAMPLE_RATE, VOSK_CHUNK_SIZE
except ImportError:
    from config import MODEL_DIR, TMP_DIR, VOSK_SAMPLE_RATE, VOSK_CHUNK_SIZE

from vosk import Model, KaldiRecognizer


def prepare_audio(input_path: str) -> str:
    """
    Конвертирует любой аудио/видео в WAV 16kHz Mono.
    Возвращает путь к временному файлу.
    """
    input_p = Path(input_path)
    output_p = TMP_DIR / f"{input_p.stem}_prepared.wav"

    cmd = [
        'ffmpeg',
        '-i', str(input_p),
        '-ar', str(VOSK_SAMPLE_RATE),
        '-ac', '1',
        '-y',
        str(output_p)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg ошибка: {result.stderr}")

    return str(output_p)


def transcribe_file(wav_path: str) -> str:
    """
    Распознаёт речь через Vosk.
    """
    # Проверка модели
    if not MODEL_DIR.exists():
        raise RuntimeError(f"Модель не найдена: {MODEL_DIR}")

    # Проверяем ключевые папки модели
    required = ['am', 'conf', 'graph']
    missing = [f for f in required if not (MODEL_DIR / f).exists()]
    if missing:
        raise RuntimeError(f"Не хватает папок в модели: {missing}")

    print(f"[INFO] Загрузка модели: {MODEL_DIR}")
    model = Model(str(MODEL_DIR))

    rec = KaldiRecognizer(model, VOSK_SAMPLE_RATE)
    rec.SetWords(False)

    text_chunks = []

    with open(wav_path, "rb") as f:
        while True:
            data = f.read(VOSK_CHUNK_SIZE)
            if not data:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                if res.get("text"):
                    text_chunks.append(res["text"])

    # Добираем остаток
    res = json.loads(rec.FinalResult())
    if res.get("text"):
        text_chunks.append(res["text"])

    return " ".join(text_chunks).strip()


def process_audio(input_path: str) -> str:
    """
    Полный цикл: файл → текст.
    """
    print(f"[INFO] Обработка: {input_path}")

    wav_path = prepare_audio(input_path)
    try:
        text = transcribe_file(wav_path)
        print(f"[INFO] Готово. Символов: {len(text)}")
        return text
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


# Тест
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование: python src/transcription.py <файл>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"Файл не найден: {file_path}")
        sys.exit(1)

    result = process_audio(file_path)
    print("\n=== РЕЗУЛЬТАТ ===")
    print(result)