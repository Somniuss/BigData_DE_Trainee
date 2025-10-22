from db.db_config import get_connection

class Database:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def insert_rooms(self, rooms):
        for room in rooms:
            self.cursor.execute(
                "INSERT INTO rooms (id, name) VALUES (%s, %s)",
                (room["id"], room["name"])
            )

    def insert_students(self, students):
        for student in students:
            self.cursor.execute(
                "INSERT INTO students (id, name, birthday, room, sex) VALUES (%s, %s, %s, %s, %s)",
                (student["id"], student["name"], student["birthday"][:10], student["room"], student["sex"])
            )

    def fetch_rooms_with_counts(self):
        self.cursor.execute("""
            SELECT r.id, r.name, COUNT(s.id) AS student_count
            FROM rooms r
            LEFT JOIN students s ON s.room = r.id
            GROUP BY r.id, r.name
        """)
        return self.cursor.fetchall()

    def commit_and_close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
