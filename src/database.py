import sqlite3
from typing import Any, Dict, List, Optional


MAX_NAME_LENGTH = 256
MAX_MESSAGE_LENGTH = 8096


class DatabaseValidationError(ValueError):
    """
    Ошибка валидации данных перед сохранением в базу.
    """
    pass


class CommentAlreadyExistsError(RuntimeError):
    """
    Ошибка при попытке добавить комментарий с уже существующим ID.
    """
    pass


class DatabaseRepository:
    """
    Репозиторий для работы с таблицей comments в SQLite.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        """
        Создаёт подключение к базе данных и таблицу, если её ещё нет.

        :param db_path: путь к файлу базы данных или ':memory:' для тестов.
        """
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        """
        Создаёт таблицу comments.
        """
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(name) <= 256),
                message TEXT NOT NULL CHECK(length(message) <= 8096)
            )
            """
        )
        self.connection.commit()

    @staticmethod
    def _ensure_comment_id(comment_id: Any) -> None:
        """
        Проверяет, что ID комментария является целым числом.
        """
        if isinstance(comment_id, bool) or not isinstance(comment_id, int):
            raise TypeError("comment_id должен быть целым числом")

    @staticmethod
    def _ensure_username(username: Any) -> None:
        """
        Проверяет, что имя пользователя является строкой.
        """
        if not isinstance(username, str):
            raise TypeError("username должен быть строкой")

    @staticmethod
    def _ensure_message(message: Any) -> None:
        """
        Проверяет, что сообщение является строкой.
        """
        if not isinstance(message, str):
            raise TypeError("message должен быть строкой")

    @classmethod
    def _validate_username(cls, username: str) -> None:
        """
        Проверяет тип и длину имени пользователя.
        """
        cls._ensure_username(username)

        if len(username) > MAX_NAME_LENGTH:
            raise DatabaseValidationError(
                f"username не должен превышать {MAX_NAME_LENGTH} символов"
            )

    @classmethod
    def _validate_message(cls, message: str) -> None:
        """
        Проверяет тип и длину сообщения.
        """
        cls._ensure_message(message)

        if len(message) > MAX_MESSAGE_LENGTH:
            raise DatabaseValidationError(
                f"message не должен превышать {MAX_MESSAGE_LENGTH} символов"
            )

    def add(self, comment_id: int, username: str, message: str) -> bool:
        """
        Добавляет новый комментарий в базу данных.

        :param comment_id: уникальный идентификатор комментария.
        :param username: имя пользователя.
        :param message: текст сообщения.
        :return: True, если запись успешно добавлена.
        """
        self._ensure_comment_id(comment_id)
        self._validate_username(username)
        self._validate_message(message)

        try:
            self.connection.execute(
                """
                INSERT INTO comments (id, name, message)
                VALUES (?, ?, ?)
                """,
                (comment_id, username, message),
            )
            self.connection.commit()
            return True

        except sqlite3.IntegrityError as exc:
            self.connection.rollback()
            raise CommentAlreadyExistsError(
                f"Комментарий с id={comment_id} уже существует"
            ) from exc

    def get_by_id(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """
        Возвращает комментарий по ID или None, если комментарий не найден.

        :param comment_id: идентификатор комментария.
        :return: словарь с данными или None.
        """
        self._ensure_comment_id(comment_id)

        row = self.connection.execute(
            """
            SELECT id, name, message
            FROM comments
            WHERE id = ?
            """,
            (comment_id,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_by_name(self, username: str) -> List[Dict[str, Any]]:
        """
        Возвращает список всех комментариев пользователя с указанным именем.

        :param username: имя пользователя.
        :return: список словарей с комментариями.
        """
        self._ensure_username(username)

        rows = self.connection.execute(
            """
            SELECT id, name, message
            FROM comments
            WHERE name = ?
            ORDER BY id
            """,
            (username,),
        ).fetchall()

        return [dict(row) for row in rows]

    def update(self, comment_id: int, new_message: str) -> bool:
        """
        Обновляет текст сообщения по ID комментария.

        :param comment_id: идентификатор комментария.
        :param new_message: новый текст сообщения.
        :return: True, если запись обновлена, иначе False.
        """
        self._ensure_comment_id(comment_id)
        self._validate_message(new_message)

        cursor = self.connection.execute(
            """
            UPDATE comments
            SET message = ?
            WHERE id = ?
            """,
            (new_message, comment_id),
        )
        self.connection.commit()

        return cursor.rowcount > 0

    def delete(self, comment_id: int) -> bool:
        """
        Удаляет комментарий по ID.

        :param comment_id: идентификатор комментария.
        :return: True, если запись удалена, иначе False.
        """
        self._ensure_comment_id(comment_id)

        cursor = self.connection.execute(
            """
            DELETE FROM comments
            WHERE id = ?
            """,
            (comment_id,),
        )
        self.connection.commit()

        return cursor.rowcount > 0

    def close(self) -> None:
        """
        Закрывает соединение с базой данных.
        """
        self.connection.close()