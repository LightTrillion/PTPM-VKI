import sys
import unittest
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы тесты могли импортировать пакет src.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database import (
    DatabaseRepository,
    DatabaseValidationError,
    CommentAlreadyExistsError,
    MAX_NAME_LENGTH,
    MAX_MESSAGE_LENGTH,
)


class TestDatabaseRepository(unittest.TestCase):

    def setUp(self) -> None:
        """
        Перед каждым тестом создаём новую базу данных в памяти.
        """
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self) -> None:
        """
        После каждого теста закрываем соединение.
        """
        self.repo.close()

    # ------------------------------------------------------------
    # Тесты метода add
    # ------------------------------------------------------------

    def test_add_success_and_get_by_id(self):
        result = self.repo.add(1, "alice", "<p>hello</p>")

        self.assertTrue(result)

        row = self.repo.get_by_id(1)

        self.assertEqual(
            row,
            {
                "id": 1,
                "name": "alice",
                "message": "<p>hello</p>",
            },
        )

    def test_add_duplicate_id_raises(self):
        self.repo.add(1, "alice", "first")

        with self.assertRaises(CommentAlreadyExistsError):
            self.repo.add(1, "bob", "second")

    def test_add_wrong_types_raise(self):
        with self.assertRaises(TypeError):
            self.repo.add("1", "alice", "message")

        with self.assertRaises(TypeError):
            self.repo.add(1, 123, "message")

        with self.assertRaises(TypeError):
            self.repo.add(1, "alice", 123)

    def test_add_too_long_fields_raise(self):
        long_name = "a" * (MAX_NAME_LENGTH + 1)
        long_message = "b" * (MAX_MESSAGE_LENGTH + 1)

        with self.assertRaises(DatabaseValidationError):
            self.repo.add(1, long_name, "ok")

        with self.assertRaises(DatabaseValidationError):
            self.repo.add(2, "ok", long_message)

    def test_add_boundary_lengths_success(self):
        name = "a" * MAX_NAME_LENGTH
        message = "b" * MAX_MESSAGE_LENGTH

        result = self.repo.add(1, name, message)

        self.assertTrue(result)

        row = self.repo.get_by_id(1)

        self.assertEqual(len(row["name"]), MAX_NAME_LENGTH)
        self.assertEqual(len(row["message"]), MAX_MESSAGE_LENGTH)

    # ------------------------------------------------------------
    # Тесты метода get_by_id
    # ------------------------------------------------------------

    def test_get_by_id_existing(self):
        self.repo.add(10, "bob", "message")

        row = self.repo.get_by_id(10)

        self.assertIsNotNone(row)
        self.assertEqual(row["id"], 10)
        self.assertEqual(row["name"], "bob")
        self.assertEqual(row["message"], "message")

    def test_get_by_id_missing_returns_none(self):
        self.assertIsNone(self.repo.get_by_id(999))

    # ------------------------------------------------------------
    # Тесты метода get_by_name
    # ------------------------------------------------------------

    def test_get_by_name_returns_all_user_comments(self):
        self.repo.add(1, "alice", "first")
        self.repo.add(2, "bob", "second")
        self.repo.add(3, "alice", "third")

        rows = self.repo.get_by_name("alice")

        self.assertEqual(len(rows), 2)

        ids = [row["id"] for row in rows]

        self.assertEqual(ids, [1, 3])

    def test_get_by_name_unknown_returns_empty_list(self):
        self.repo.add(1, "alice", "first")

        rows = self.repo.get_by_name("unknown")

        self.assertEqual(rows, [])

    # ------------------------------------------------------------
    # Тесты метода update
    # ------------------------------------------------------------

    def test_update_existing_changes_message(self):
        self.repo.add(1, "alice", "old message")

        result = self.repo.update(1, "new message")

        self.assertTrue(result)

        row = self.repo.get_by_id(1)

        self.assertEqual(row["message"], "new message")

    def test_update_missing_returns_false(self):
        result = self.repo.update(999, "new message")

        self.assertFalse(result)

    def test_update_too_long_message_raises(self):
        self.repo.add(1, "alice", "old message")

        long_message = "b" * (MAX_MESSAGE_LENGTH + 1)

        with self.assertRaises(DatabaseValidationError):
            self.repo.update(1, long_message)

    def test_update_wrong_type_raises(self):
        self.repo.add(1, "alice", "old message")

        with self.assertRaises(TypeError):
            self.repo.update(1, 12345)

    # ------------------------------------------------------------
    # Тесты метода delete
    # ------------------------------------------------------------

    def test_delete_existing_returns_true_and_removes(self):
        self.repo.add(1, "alice", "message")

        result = self.repo.delete(1)

        self.assertTrue(result)
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_missing_returns_false(self):
        result = self.repo.delete(999)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()