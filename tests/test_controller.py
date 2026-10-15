"""
Интеграционные тесты для класса Controller.

Проверяется сквозной сценарй:
    UI (заглушка) → DB → Calculator → ExternalService (заглушка)

Используются тестовые заглушки (Mock) для имитации
пользовательского ввода и отправки данных на внешний сервер.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from triangle_calculator import TriangleCalculator
from database import TriangleDatabase
from controller import Controller


class TestController(unittest.TestCase):
    """
    Интеграционные тесты контроллера.
    Проверяют взаимодействие Calculator + Database + ExternalService
    через контроллер с подменённым UI.
    """

    def setUp(self):
        """Создаём реальные компоненты и заглушки для UI и ExternalService."""
        self.calculator = TriangleCalculator()
        self.database = TriangleDatabase(":memory:")
        self.ui = Mock()
        self.external_service = Mock()
        self.external_service.send.return_value = True

        self.controller = Controller(
            calculator=self.calculator,
            database=self.database,
            user_interface=self.ui,
            external_service=self.external_service,
        )

    def tearDown(self):
        self.database.close()

    def test_new_triangle_calculated_and_stored_in_db(self):
        """
        Сценарий: треугольник вычисляется и сохраняется в БД.
        Пользователь вводит 3, 4, 5 → результат вычисляется и добавляется в БД.
        """
        # Заглушка UI возвращает стороны 3, 4, 5
        self.ui.get_triangle_sides.return_value = ("3", "4", "5")

        result = self.controller.run()

        # Проверяем, что результат вычислен
        self.assertEqual(result["type"], "разносторонний")
        self.assertEqual(result["source"], "calculated")

        # Проверяем, что запись добавлена в БД
        db_record = self.database.get_record(3.0, 4.0, 5.0)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record["triangle_type"], "разносторонний")

        # Проверяем, что результат отправлен сторонней зависимости
        self.external_service.send.assert_called_once()
        sent_message = self.external_service.send.call_args[0][0]
        self.assertIn("разносторонний", sent_message)

    def test_existing_triangle_taken_from_db(self):
        """
        Сценарий: повторный ввод тех же сторон — результат берётся из БД.
        """
        # Сначала добавляем запись в БД
        self.database.add_record(1.0, 1.0, 1.0, "равносторонний", None)

        # Заглушка UI возвращает те же стороны
        self.ui.get_triangle_sides.return_value = ("1", "1", "1")

        result = self.controller.run()

        # Проверяем, что результат взят из БД, а не вычислен заново
        self.assertEqual(result["type"], "равносторонний")
        self.assertEqual(result["source"], "database")

        # Проверяем, что результат отправлен
        self.external_service.send.assert_called_once()

    def test_invalid_input_returns_error_result(self):
        """
        Сценарий: невалидные данные — возвращается результат с ошибкой.
        """
        # Заглушка UI возвращает нечисловые данные
        self.ui.get_triangle_sides.return_value = ("abc", "4", "5")

        result = self.controller.run()

        # Проверяем, что результат содержит ошибку
        self.assertEqual(result["type"], "")
        self.assertIsNotNone(result["error"])

        # Проверяем, что результат отправлен сторонней зависимости
        self.external_service.send.assert_called_once()
        sent_message = self.external_service.send.call_args[0][0]
        self.assertIn("Ошибка", sent_message)

    def test_external_service_called_with_correct_message(self):
        """
        Сценарий: сторонняя зависимость вызывается с корректным сообщением.
        """
        self.ui.get_triangle_sides.return_value = ("3", "4", "5")

        self.controller.run()

        # Проверяем аргумент вызова
        self.external_service.send.assert_called_once()
        sent_message = self.external_service.send.call_args[0][0]
        self.assertIn("Тип треугольника", sent_message)
        self.assertIn("разносторонний", sent_message)

    def test_ui_show_result_called(self):
        """
        Сценарий: результат отображается пользователю через UI.
        """
        self.ui.get_triangle_sides.return_value = ("5", "5", "3")

        self.controller.run()

        # Проверяем, что UI был вызван для отображения результата
        self.ui.show_result.assert_called_once()
        shown_result = self.ui.show_result.call_args[0][0]
        self.assertEqual(shown_result["type"], "равнобедренный")


if __name__ == "__main__":
    unittest.main()
