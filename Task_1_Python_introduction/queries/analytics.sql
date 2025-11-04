-- 1. Список комнат и количество студентов
SELECT
    r.id,
    r.name,
    COUNT(s.id) AS student_count
FROM rooms r
LEFT JOIN students s ON s.room = r.id
GROUP BY r.id, r.name
ORDER BY student_count DESC;

-- 2. 5 комнат с самым маленьким средним возрастом студентов
SELECT
    r.id,
    r.name,
    AVG(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE())) AS avg_age
FROM rooms r
JOIN students s ON s.room = r.id
GROUP BY r.id, r.name
ORDER BY avg_age ASC
LIMIT 5;

-- 3. 5 комнат с самой большой разницей в возрасте студентов
SELECT
    r.id,
    r.name,
    (MAX(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE()))
     - MIN(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE()))) AS age_diff
FROM rooms r
JOIN students s ON s.room = r.id
GROUP BY r.id, r.name
ORDER BY age_diff DESC
LIMIT 5;

-- 4. Список комнат с разнополыми студентами
SELECT
    r.id,
    r.name
FROM rooms r
JOIN students s ON s.room = r.id
GROUP BY r.id, r.name
HAVING COUNT(DISTINCT s.sex) > 1;

-- 5. Индексы для оптимизации запросов
CREATE INDEX idx_students_room ON students(room);
CREATE INDEX idx_students_birthday ON students(birthday);
CREATE INDEX idx_students_sex_room ON students(sex, room);
