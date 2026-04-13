from llm_client import LLMClient

print("Проверка подключения")
client = LLMClient()
if client.check_connection():
    print("- LM Studio доступен")
else:
    print("- LM Studio не доступен")
    exit(1)

print("\nТест процессоров")

# Тест саммари
from processors.summary_gen import generate_summary
summary = generate_summary("Обсуждали бюджет. Решили увеличить на 10%.")
print(f"- Саммари: {len(summary)} символов")

# Тест задач
from processors.task_extractor import extract_tasks
tasks = extract_tasks("Иванов сделает отчёт до пятницы.")
print(f"- Задачи: {tasks.get('total_tasks', 0)} найдено")

print("\nГотово")