import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import OUTPUT_DIR
from transcription import process_audio
from llm_client import LLMClient
from processors.summary_gen import generate_summary
from processors.protocol_gen import generate_protocol
from processors.task_extractor import extract_tasks, save_tasks
from processors.roles_marker import mark_roles

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def save_result(content: str, filename: str, subdir: str):
    output_path = OUTPUT_DIR / subdir / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Сохранено: {output_path}")
    return str(output_path)


def process_meeting(audio_path: str, meeting_id: str = None):
    start_time = datetime.now()
    logger.info(f"=== Начало обработки ===")
    logger.info(f"Файл: {audio_path}")

    if not meeting_id:
        meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    client = LLMClient()
    if not client.check_connection():
        raise RuntimeError("LM не доступен, запусти сервер в LM Studio.")
    logger.info("- LMStudio подключён")

    logger.info("\n[1/5] Транскрибация...")
    transcript = process_audio(audio_path)
    transcript_path = save_result(transcript, f"{meeting_id}_transcript.txt", "transcripts")
    logger.info(f"- Текст: {len(transcript)} символов")

    logger.info("\n[2/5] Распределение ролей...")
    roles_data = mark_roles(transcript)
    roles_path = save_result(json.dumps(roles_data, ensure_ascii=False, indent=2),
                f"{meeting_id}_roles.json", "transcripts")
    participants = [p.get("name", "Неизвестный") for p in roles_data.get("participants", [])]
    logger.info(f"- Участники: {len(participants)} чел.")

    logger.info("\n[3/5] Генерация саммари...")
    summary = generate_summary(transcript)
    summary_path = save_result(summary, f"{meeting_id}_summary.txt", "summaries")
    logger.info(f"- Саммари: {len(summary)} символов")

    logger.info("\n[4/5] Создание протокола...")
    protocol = generate_protocol(transcript, participants)
    protocol_path = save_result(protocol, f"{meeting_id}_protocol.md", "protocols")
    logger.info(f"- Протокол: {len(protocol)} символов")

    logger.info("\n[5/5] Извлечение задач...")
    tasks_data = extract_tasks(transcript)
    tasks_path = save_tasks(tasks_data, str(OUTPUT_DIR / "tasks" / f"{meeting_id}_tasks.json"))
    logger.info(f"- Задачи: {tasks_data.get('total_tasks', 0)} найдено")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info(f"\nОбработка завершена")
    logger.info(f"Время: {duration:.1f} сек")
    logger.info(f"Результаты в: {OUTPUT_DIR}")

    return {
        "meeting_id": meeting_id,
        "transcript_len": len(transcript),
        "participants_count": len(participants),
        "tasks_count": tasks_data.get('total_tasks', 0),
        "duration_sec": duration,
        "output_dir": str(OUTPUT_DIR),
        "transcript_path": transcript_path,
        "summary_path": summary_path,
        "protocol_path": protocol_path,
        "tasks_path": tasks_path,
    }


if __name__ == "__main__":
    print("=" * 50)
    print("ЦИФРОВОЙ АССИСТЕНТ — ОБРАБОТКА СОВЕЩАНИЙ")
    print("Банк Уралсиб | Hackathon 2026")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("\nИспользование: python src/main.py <путь_к_аудио> [ID_встречи]")
        print("\nПримеры:")
        print("  python src/main.py data/input/meeting.mp4")
        print("  python src/main.py data/input/meeting.mp4 meeting_001")
        sys.exit(1)

    audio_file = sys.argv[1]
    meeting_id = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(audio_file).exists():
        print(f"\nФайл не найден: {audio_file}")
        sys.exit(1)

    try:
        result = process_meeting(audio_file, meeting_id)
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТ:")
        print(f"  ID встречи: {result['meeting_id']}")
        print(f"  Транскрибат: {result['transcript_len']} символов")
        print(f"  Участники: {result['participants_count']} чел.")
        print(f"  Задачи: {result['tasks_count']}")
        print(f"  Время обработки: {result['duration_sec']:.1f} сек")
        print(f"  Вывод: {result['output_dir']}")
        print("=" * 50)
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)