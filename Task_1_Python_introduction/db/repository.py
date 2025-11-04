from abc import ABC, abstractmethod

class BaseRepository(ABC):
    """Абстрактный базовый класс для всех репозиториев"""

    @abstractmethod
    def insert(self, items):
        """Метод вставки данных"""
        pass

    @abstractmethod
    def fetch_all(self):
        """Метод получения всех данных"""
        pass
