from db.database import Database
from db.repository import BaseRepository

class StudentRepository(BaseRepository):
    def __init__(self, db: Database):
        self.db = db

    def insert(self, students):
        """
        Вставка студентов в таблицу.
        Используем batch insert для ускорения.
        """
        data = [
            (s["id"], s["name"], s["birthday"][:10], s["room"], s["sex"])
            for s in students
        ]
        self.db.cursor.executemany(
            "INSERT INTO students (id, name, birthday, room, sex) VALUES (%s, %s, %s, %s, %s)",
            data
        )

    def fetch_all(self):
        """Получить всех студентов"""
        self.db.cursor.execute("SELECT * FROM students")
        return self.db.cursor.fetchall()

    def fetch_by_room(self, room_id):
        """Получить студентов по id комнаты"""
        self.db.cursor.execute(
            "SELECT * FROM students WHERE room = %s",
            (room_id,)
        )
        return self.db.cursor.fetchall()

    def fetch_average_age_by_room(self):
        """
        Получить средний возраст студентов по каждой комнате
        Возраст считается по году рождения до текущей даты
        """
        self.db.cursor.execute("""
            SELECT room, AVG(TIMESTAMPDIFF(YEAR, birthday, CURDATE())) AS avg_age
            FROM students
            GROUP BY room
        """)
        return self.db.cursor.fetchall()

    def fetch_age_diff_by_room(self):
        """
        Получить разницу между самым старшим и самым младшим студентом в комнате
        """
        self.db.cursor.execute("""
            SELECT room,
                   (MAX(TIMESTAMPDIFF(YEAR, birthday, CURDATE())) - 
                    MIN(TIMESTAMPDIFF(YEAR, birthday, CURDATE()))) AS age_diff
            FROM students
            GROUP BY room
        """)
        return self.db.cursor.fetchall()

    def fetch_mixed_gender_rooms(self):
        """
        Получить комнаты, где есть студенты разного пола
        """
        self.db.cursor.execute("""
            SELECT room
            FROM students
            GROUP BY room
            HAVING COUNT(DISTINCT sex) > 1
        """)
        return self.db.cursor.fetchall()
