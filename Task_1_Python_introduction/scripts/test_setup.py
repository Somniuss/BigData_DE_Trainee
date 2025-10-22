import sys
import traceback

print("🔹 Проверка проекта Task_1_Python_introduction")

# Проверка импорта
try:
    from loaders.json_loader import JSONLoader
    from db.database import Database
    from db.room_repository import RoomRepository
    from db.student_repository import StudentRepository
    from exporters.exporter import Exporter
    print("✅ Все импорты успешно выполнены")
except ImportError as e:
    print("❌ Ошибка импорта:", e)
    sys.exit(1)

# Проверка загрузки JSON
try:
    rooms_data = JSONLoader.load("data/rooms.json")
    students_data = JSONLoader.load("data/students.json")
    print(f"✅ JSON загружен: {len(rooms_data)} комнат, {len(students_data)} студентов")
except Exception as e:
    print("❌ Ошибка при загрузке JSON:", e)
    sys.exit(1)

# Проверка подключения к БД
try:
    db = Database()
    cursor = db.cursor
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print("✅ Подключение к MySQL успешно, тестовый запрос вернул:", result)
    db.commit_and_close()
except Exception as e:
    print("❌ Ошибка подключения к БД или выполнения запроса:", e)
    traceback.print_exc()
    sys.exit(1)

# Проверка создания репозиториев
try:
    db = Database()
    room_repo = RoomRepository(db)
    student_repo = StudentRepository(db)
    print("✅ Репозитории созданы успешно")
    db.commit_and_close()
except Exception as e:
    print("❌ Ошибка создания репозиториев:", e)
    sys.exit(1)

print("🎉 Все проверки пройдены! Проект готов к запуску.")
