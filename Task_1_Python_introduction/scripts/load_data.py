import argparse
from loaders.json_loader import JSONLoader
from db.database import Database
from db.room_repository import RoomRepository
from db.student_repository import StudentRepository
from exporters.exporter import Exporter

def main():
    parser = argparse.ArgumentParser(description="Load JSON into MySQL and export analytics")
    parser.add_argument("--students", required=True, help="Path to students JSON")
    parser.add_argument("--rooms", required=True, help="Path to rooms JSON")
    parser.add_argument("--format", choices=["json", "xml"], default="json", help="Output format")
    args = parser.parse_args()

    # 1. Загружаем JSON
    rooms = JSONLoader.load(args.rooms)
    students = JSONLoader.load(args.students)

    # 2. Подключаемся к БД
    db = Database()
    room_repo = RoomRepository(db)
    student_repo = StudentRepository(db)

    # 2.1 Очистка таблиц перед вставкой
    db.cursor.execute("DELETE FROM students")
    db.cursor.execute("DELETE FROM rooms")
    db.conn.commit()

    # 2.2 Вставка новых данных
    room_repo.insert(rooms)
    student_repo.insert(students)
    db.conn.commit()

    # 3. Выполняем все аналитические запросы
    analytics_results = {}

    # 3.1 Количество студентов в каждой комнате
    analytics_results["room_counts"] = room_repo.fetch_rooms_with_counts()

    # 3.2 5 комнат с самым маленьким средним возрастом
    analytics_results["top5_youngest_avg_age"] = room_repo.fetch_top5_smallest_avg_age()

    # 3.3 5 комнат с самой большой разницей в возрасте
    analytics_results["top5_largest_age_diff"] = room_repo.fetch_top5_largest_age_diff()

    # 3.4 Комнаты с разнополыми студентами
    analytics_results["mixed_gender_rooms"] = room_repo.fetch_mixed_gender_rooms()

    # 4. Закрываем соединение
    db.commit_and_close()

    # 5. Экспорт в JSON или XML
    if args.format == "json":
        print(Exporter.to_json(analytics_results))
    else:
        print(Exporter.to_xml(analytics_results, root_name="analytics", item_name="result"))

if __name__ == "__main__":
    main()
