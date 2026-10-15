"""Юнит-тесты для класса TriangleDatabase."""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from database import TriangleDatabase


class TestTriangleDatabase(unittest.TestCase):
    """Тесты класса работы с базой данных TriangleDatabase."""

    def setUp(self):
        """Каждый тест получает чистую БД в памяти."""
        self.db = TriangleDatabase(":memory:")

    def tearDown(self):
        self.db.close()

    def test_add_and_get_record(self):
        """Запись добавляется и находится по трём сторонам."""
        self.db.add_record(3.0, 4.0, 5.0, "разносторонний", None)
        record = self.db.get_record(3.0, 4.0, 5.0)
        self.assertIsNotNone(record)
        self.assertEqual(record["triangle_type"], "разносторонний")
        self.assertIsNone(record["error_message"])

    def test_get_record_returns_none_for_missing(self):
        """Поиск несуществующей записи возвращает None."""
        record = self.db.get_record(99.0, 99.0, 99.0)
        self.assertIsNone(record)

    def test_add_record_with_error_message(self):
        """Запись с сообщением об ошибке сохраняется корректно."""
        self.db.add_record(1.0, 1.0, 10.0, "не треугольник", "Ошибка: неравенство")
        record = self.db.get_record(1.0, 1.0, 10.0)
        self.assertIsNotNone(record)
        self.assertEqual(record["triangle_type"], "не треугольник")
        self.assertEqual(record["error_message"], "Ошибка: неравенство")

    def test_delete_existing_record(self):
        """Существующая запись удаляется успешно."""
        self.db.add_record(3.0, 4.0, 5.0, "разносторонний", None)
        deleted = self.db.delete_record(3.0, 4.0, 5.0)
        self.assertTrue(deleted)
        self.assertIsNone(self.db.get_record(3.0, 4.0, 5.0))

    def test_delete_nonexistent_record_returns_false(self):
        """Удаление несуществующей записи возвращает False."""
        deleted = self.db.delete_record(99.0, 99.0, 99.0)
        self.assertFalse(deleted)

    def test_get_all_records(self):
        """Все записи возвращаются корректно."""
        self.db.add_record(1.0, 1.0, 1.0, "равносторонний", None)
        self.db.add_record(3.0, 4.0, 5.0, "разносторонний", None)
        records = self.db.get_all_records()
        self.assertEqual(len(records), 2)

    def test_clear_removes_all_records(self):
        """Очистка таблицы удаляет все записи."""
        self.db.add_record(1.0, 1.0, 1.0, "равносторонний", None)
        self.db.add_record(3.0, 4.0, 5.0, "разносторонний", None)
        self.db.clear()
        self.assertEqual(len(self.db.get_all_records()), 0)

    def test_record_identified_by_three_lengths(self):
        """Запись идентифицируется строго по трём сторонам."""
        self.db.add_record(3.0, 4.0, 5.0, "разносторонний", None)
        # Другой порядок сторон — другая запись
        record = self.db.get_record(4.0, 3.0, 5.0)
        self.assertIsNone(record)


if __name__ == "__main__":
    unittest.main()
