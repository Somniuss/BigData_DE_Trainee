from db.database import Database
from db.repository import BaseRepository


class RoomRepository(BaseRepository):
    def __init__(self, db: Database):
        self.db = db

    def insert(self, rooms):
        for room in rooms:
            self.db.cursor.execute(
                "INSERT INTO rooms (id, name) VALUES (%s, %s)",
                (room["id"], room["name"])
            )
        # сохраняем изменения
        self.db.connection.commit()

    def fetch_all(self):
        self.db.cursor.execute("SELECT * FROM rooms")
        return self.db.cursor.fetchall()

    def fetch_rooms_with_counts(self):
        self.db.cursor.execute("""
            SELECT r.id, r.name, COUNT(s.id) AS student_count
            FROM rooms r
            LEFT JOIN students s ON s.room = r.id
            GROUP BY r.id, r.name
        """)
        return self.db.cursor.fetchall()

    def fetch_top5_smallest_avg_age(self):
        self.db.cursor.execute("""
            SELECT r.id, r.name, AVG(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE())) AS avg_age
            FROM rooms r
            JOIN students s ON s.room = r.id
            GROUP BY r.id, r.name
            ORDER BY avg_age ASC
            LIMIT 5
        """)
        return self.db.cursor.fetchall()

    def fetch_top5_largest_age_diff(self):
        self.db.cursor.execute("""
            SELECT r.id, r.name,
                   (MAX(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE())) -
                    MIN(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE()))) AS age_diff
            FROM rooms r
            JOIN students s ON s.room = r.id
            GROUP BY r.id, r.name
            ORDER BY age_diff DESC
            LIMIT 5
        """)
        return self.db.cursor.fetchall()

    def fetch_mixed_gender_rooms(self):
        self.db.cursor.execute("""
            SELECT r.id, r.name
            FROM rooms r
            JOIN students s ON s.room = r.id
            GROUP BY r.id, r.name
            HAVING COUNT(DISTINCT s.sex) > 1
        """)
        return self.db.cursor.fetchall()
