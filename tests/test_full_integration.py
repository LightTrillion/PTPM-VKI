"""
Сквозной интеграционный тест: проверка всей цепочки целиком.

Используются реальные компоненты:
    - TriangleCalculator (реальный)
    - TriangleDatabase (реальный, SQLite в памяти)
    - ConsoleUI (реальный, но input() заменён заглушкой)
    - EmailService (реальный, но send() заменён заглушкой)
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from triangle_calculator import TriangleCalculator
from database import TriangleDatabase
from user_interface import ConsoleUI
from external_service import EmailService
from controller import Controller


class TestFullIntegration(unittest.TestCase):
    """
    Сквозные интеграционные тесты.
    Проверяют полную цепочку: UI → Controller → DB/Calculator → ExternalService.
    """

    def setUp(self):
        """Собираем реальные компоненты."""
        self.calculator = TriangleCalculator()
        self.database = TriangleDatabase(":memory:")
        self.ui = ConsoleUI()
        self.email_service = EmailService()
        self.email_service.connect()

        self.controller = Controller(
            calculator=self.calculator,
            database=self.database,
            user_interface=self.ui,
            external_service=self.email_service,
        )

    def tearDown(self):
        self.database.close()

    @patch("builtins.input", side_effect=["3", "4", "5"])
    @patch("builtins.print")
    def test_full_flow_new_triangle(self, mock_print, mock_input):
        """
        Полный сценарий: новый треугольник 3-4-5.
        Проверяет, что результат вычислен, сохранён в БД и отправлен.
        """
        result = self.controller.run()

        # Результат вычислен
        self.assertEqual(result["type"], "разносторонний")
        self.assertEqual(result["source"], "calculated")

        # Запись добавлена в БД
        db_record = self.database.get_record(3.0, 4.0, 5.0)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record["triangle_type"], "разносторонний")

        # Сообщение отправлено через EmailService
        messages = self.email_service.get_sent_messages()
        self.assertEqual(len(messages), 1)
        self.assertIn("разносторонний", messages[0])

    @patch("builtins.input", side_effect=["3", "4", "5", "3", "4", "5"])
    @patch("builtins.print")
    def test_full_flow_second_run_uses_cache(self, mock_print, mock_input):
        """
        Полный сценарий: повторный ввод тех же сторон.
        Второй запуск должен взять результат из БД, а не вычислять заново.
        """
        # Первый запуск
        result1 = self.controller.run()
        self.assertEqual(result1["source"], "calculated")

        # Второй запуск с теми же сторонами
        result2 = self.controller.run()
        self.assertEqual(result2["type"], "разносторонний")
        self.assertEqual(result2["source"], "database")

        # EmailService получил два сообщения
        messages = self.email_service.get_sent_messages()
        self.assertEqual(len(messages), 2)

    @patch("builtins.input", side_effect=["abc", "4", "5"])
    @patch("builtins.print")
    def test_full_flow_invalid_input(self, mock_print, mock_input):
        """
        Полный сценарий: невалидные данные.
        Результат должен содержать ошибку и быть отправлен.
        """
        result = self.controller.run()

        self.assertEqual(result["type"], "")
        self.assertIsNotNone(result["error"])

        # Сообщение об ошибке отправлено
        messages = self.email_service.get_sent_messages()
        self.assertEqual(len(messages), 1)
        self.assertIn("Ошибка", messages[0])


if __name__ == "__main__":
    unittest.main()
