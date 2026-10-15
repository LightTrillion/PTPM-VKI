"""Юнит-тесты для классов UserInterface и ConsoleUI."""

import unittest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from user_interface import UserInterface, ConsoleUI


class TestUserInterface(unittest.TestCase):
    """Тесты абстрактного класса и консольной реализации."""

    def test_cannot_instantiate_abstract_class(self):
        """Нельзя создать экземпляр абстрактного класса."""
        with self.assertRaises(TypeError):
            UserInterface()

    @patch("builtins.input", side_effect=["3", "4", "5"])
    def test_console_ui_reads_three_sides(self, mock_input):
        """ConsoleUI запрашивает три стороны через input()."""
        ui = ConsoleUI()
        a, b, c = ui.get_triangle_sides()
        self.assertEqual(a, "3")
        self.assertEqual(b, "4")
        self.assertEqual(c, "5")
        self.assertEqual(mock_input.call_count, 3)

    @patch("builtins.input", side_effect=["abc", "4", "5"])
    def test_console_ui_returns_raw_strings(self, mock_input):
        """ConsoleUI возвращает строки без преобразования."""
        ui = ConsoleUI()
        a, b, c = ui.get_triangle_sides()
        self.assertEqual(a, "abc")
        self.assertEqual(b, "4")
        self.assertEqual(c, "5")

    @patch("builtins.print")
    def test_show_result_prints_type(self, mock_print):
        """show_result выводит тип треугольника."""
        ui = ConsoleUI()
        result = {"type": "равносторонний", "error": None, "vertices": None}
        ui.show_result(result)
        mock_print.assert_called_once()
        printed = mock_print.call_args[0][0]
        self.assertIn("равносторонний", printed)

    @patch("builtins.print")
    def test_show_error_prints_message(self, mock_print):
        """show_error выводит сообщение об ошибке."""
        ui = ConsoleUI()
        ui.show_error("Тестовая ошибка")
        mock_print.assert_called_once()
        printed = mock_print.call_args[0][0]
        self.assertIn("Тестовая ошибка", printed)


if __name__ == "__main__":
    unittest.main()
