CREATE TABLE IF NOT EXISTS rooms (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Для students: используем ENUM('M','F') для простоты и совместимости MySQL
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    birthday DATE NOT NULL,
    room INT,
    sex ENUM('M','F') DEFAULT 'M',
    CONSTRAINT fk_room FOREIGN KEY (room) REFERENCES rooms(id)
      ON DELETE SET NULL
      ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
