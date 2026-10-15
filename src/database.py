"""Класс работы с базой данных SQLite для хранения результатов вычислений."""

import sqlite3
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TriangleDatabase:
    """
    Класс работы с базой данных (SQLite).

    Одна запись БД содержит:
        - длина1, длина2, длина3 — стороны треугольника (идентификатор записи)
        - тип_треугольника — результат вычисления
        - сообщение_об_ошибке — сообщение об ошибке (если она есть)
    """

    def __init__(self, db_path: str = ":memory:"):
        """
        Args:
            db_path: путь к файлу БД (по умолчанию — БД в памяти)
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_table()
        logger.info("База данных инициализирована: %s", db_path)

    def _create_table(self):
        """Создаёт таблицу, если она не существует."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS triangles (
                length1 REAL NOT NULL,
                length2 REAL NOT NULL,
                length3 REAL NOT NULL,
                triangle_type TEXT NOT NULL,
                error_message TEXT,
                PRIMARY KEY (length1, length2, length3)
            )
            """
        )
        self.connection.commit()

    def add_record(
        self,
        length1: float,
        length2: float,
        length3: float,
        triangle_type: str,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Добавляет запись в БД.

        Returns:
            True если запись добавлена, False если такая запись уже существует
        """
        try:
            self.connection.execute(
                """
                INSERT OR IGNORE INTO triangles
                    (length1, length2, length3, triangle_type, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (length1, length2, length3, triangle_type, error_message),
            )
            self.connection.commit()
            logger.info(
                "Добавлена запись: %s, %s, %s -> %s",
                length1, length2, length3, triangle_type,
            )
            return True
        except sqlite3.Error as e:
            logger.error("Ошибка при добавлении записи: %s", e)
            return False

    def get_record(
        self, length1: float, length2: float, length3: float
    ) -> Optional[dict]:
        """
        Получает запись из БД по трём сторонам.

        Returns:
            dict с данными записи или None, если запись не найдена
        """
        cursor = self.connection.execute(
            """
            SELECT length1, length2, length3, triangle_type, error_message
            FROM triangles
            WHERE length1 = ? AND length2 = ? AND length3 = ?
            """,
            (length1, length2, length3),
        )
        row = cursor.fetchone()
        if row is None:
            logger.debug(
                "Запись не найдена: %s, %s, %s", length1, length2, length3
            )
            return None
        result = {
            "length1": row["length1"],
            "length2": row["length2"],
            "length3": row["length3"],
            "triangle_type": row["triangle_type"],
            "error_message": row["error_message"],
        }
        logger.debug("Найдена запись: %s", result)
        return result

    def delete_record(
        self, length1: float, length2: float, length3: float
    ) -> bool:
        """
        Удаляет запись из БД.

        Returns:
            True если запись удалена, False если запись не найдена
        """
        cursor = self.connection.execute(
            """
            DELETE FROM triangles
            WHERE length1 = ? AND length2 = ? AND length3 = ?
            """,
            (length1, length2, length3),
        )
        self.connection.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(
                "Удалена запись: %s, %s, %s", length1, length2, length3
            )
        else:
            logger.warning(
                "Запись для удаления не найдена: %s, %s, %s",
                length1, length2, length3,
            )
        return deleted

    def get_all_records(self) -> list:
        """Возвращает все записи из БД."""
        cursor = self.connection.execute("SELECT * FROM triangles")
        return [dict(row) for row in cursor.fetchall()]

    def clear(self):
        """Очищает таблицу."""
        self.connection.execute("DELETE FROM triangles")
        self.connection.commit()
        logger.info("Таблица очищена")

    def close(self):
        """Закрывает соединение с БД."""
        self.connection.close()
        logger.info("Соединение с БД закрыто")
