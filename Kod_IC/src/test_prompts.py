from prompts import load_prompt

print("=== Проверка промптов ===\n")

for name in ["roles", "summary", "protocol", "tasks"]:
    try:
        prompt = load_prompt(name)
        print(f"- {name}.txt — {len(prompt)} символов")
    except Exception as e:
        print(f"- {name}.txt — ошибка: {e}")

print("\n=== Готово ===")