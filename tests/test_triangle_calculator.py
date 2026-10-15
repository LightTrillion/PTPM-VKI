"""Юнит-тесты для класса TriangleCalculator."""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from triangle_calculator import TriangleCalculator


class TestTriangleCalculator(unittest.TestCase):
    """Тесты класса вычислений TriangleCalculator."""

    def setUp(self):
        self.calc = TriangleCalculator()

    def test_equilateral_triangle_returns_correct_type(self):
        """Равносторонний треугольник определяется корректно."""
        result = self.calc.calculate(1, 1, 1)
        self.assertEqual(result["type"], "равносторонний")
        self.assertIsNone(result["error"])

    def test_isosceles_triangle_returns_correct_type(self):
        """Равнобедренный треугольник определяется корректно."""
        result = self.calc.calculate(5, 5, 3)
        self.assertEqual(result["type"], "равнобедренный")
        self.assertIsNone(result["error"])

    def test_scalene_triangle_returns_correct_type(self):
        """Разносторонний треугольник определяется корректно."""
        result = self.calc.calculate(3, 4, 5)
        self.assertEqual(result["type"], "разносторонний")
        self.assertIsNone(result["error"])

    def test_non_triangle_returns_error(self):
        """Стороны, не образующие треугольник, возвращают ошибку."""
        result = self.calc.calculate(1, 1, 10)
        self.assertEqual(result["type"], "не треугольник")
        self.assertIsNotNone(result["error"])

    def test_non_numeric_input_returns_empty_type(self):
        """Нечисловые данные возвращают пустой тип."""
        result = self.calc.calculate("abc", 4, 5)
        self.assertEqual(result["type"], "")
        self.assertIsNotNone(result["error"])

    def test_negative_side_returns_not_triangle(self):
        """Отрицательная сторона возвращает 'не треугольник'."""
        result = self.calc.calculate(-3, 4, 5)
        self.assertEqual(result["type"], "не треугольник")
        self.assertIsNotNone(result["error"])

    def test_zero_side_returns_not_triangle(self):
        """Нулевая сторона возвращает 'не треугольник'."""
        result = self.calc.calculate(0, 4, 5)
        self.assertEqual(result["type"], "не треугольник")
        self.assertIsNotNone(result["error"])

    def test_float_sides_processed_correctly(self):
        """Дробные стороны обрабатываются корректно."""
        result = self.calc.calculate(1.5, 1.5, 1.5)
        self.assertEqual(result["type"], "равносторонний")
        self.assertIsNone(result["error"])

    def test_string_numbers_processed_correctly(self):
        """Числа в виде строк обрабатываются корректно."""
        result = self.calc.calculate("3", "4", "5")
        self.assertEqual(result["type"], "разносторонний")
        self.assertIsNone(result["error"])

    def test_none_input_returns_empty_type(self):
        """None на входе возвращает пустой тип."""
        result = self.calc.calculate(None, 4, 5)
        self.assertEqual(result["type"], "")
        self.assertIsNotNone(result["error"])

    def test_degenerate_triangle_returns_not_triangle(self):
        """Вырожденный треугольник (a+b=c) возвращает 'не треугольник'."""
        result = self.calc.calculate(1, 2, 3)
        self.assertEqual(result["type"], "не треугольник")
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
