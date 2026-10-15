"""Класс вычислений: определение типа треугольника по трём сторонам."""

import math
import logging

logger = logging.getLogger(__name__)


class TriangleCalculator:
    """
    Класс вычислений/валидации.
    Метод calculate() принимает три стороны треугольника и возвращает словарь
    с результатом: тип треугольника или сообщение об ошибке.
    """

    def calculate(self, a, b, c) -> dict:
        """
        Определяет, является ли тройка (a, b, c) треугольником.

        Args:
            a: первая сторона (число)
            b: вторая сторона (число)
            c: третья сторона (число)

        Returns:
            dict с ключами:
                - "type": str — тип треугольника
                  ("равносторонний", "равнобедренный", "разносторонний",
                   "не треугольник", "")
                - "error": str | None — сообщение об ошибке (если есть)
                - "vertices": list — координаты вершин (если вычислены)
        """
        logger.debug("Вычисление для сторон: %s, %s, %s", a, b, c)

        # Проверка на числовые данные
        values = self._to_float(a), self._to_float(b), self._to_float(c)
        if any(v is None for v in values):
            logger.error("Невалидные (нечисловые) данные: %s, %s, %s", a, b, c)
            return {
                "type": "",
                "error": "Невалидные (нечисловые) данные",
                "vertices": [(-2, -2), (-2, -2), (-2, -2)],
            }

        fa, fb, fc = values

        # Проверка на корректные числа (> 0, конечные)
        if any(v <= 0 or not math.isfinite(v) for v in values):
            logger.error("Ошибочные числовые данные: %s, %s, %s", a, b, c)
            return {
                "type": "не треугольник",
                "error": "Стороны должны быть положительными конечными числами",
                "vertices": [(-1, -1), (-1, -1), (-1, -1)],
            }

        # Проверка неравенства треугольника
        if not self._is_triangle(fa, fb, fc):
            logger.warning(
                "Стороны не образуют треугольник: %s, %s, %s", fa, fb, fc
            )
            return {
                "type": "не треугольник",
                "error": "Стороны не удовлетворяют неравенству треугольника",
                "vertices": [(-1, -1), (-1, -1), (-1, -1)],
            }

        # Классификация
        tri_type = self._classify(fa, fb, fc)
        logger.info(
            "Успех: %s, %s, %s -> '%s'", fa, fb, fc, tri_type
        )
        return {
            "type": tri_type,
            "error": None,
            "vertices": None,
        }

    @staticmethod
    def _to_float(value):
        """Пытается преобразовать значение в float. Возвращает None при ошибке."""
        if value is None:
            return None
        try:
            return float(str(value).strip())
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _is_triangle(a, b, c, eps=1e-9):
        """Проверка неравенства треугольника."""
        return (a + b > c + eps) and (a + c > b + eps) and (b + c > a + eps)

    @staticmethod
    def _classify(a, b, c, eps=1e-6):
        """Классификация треугольника по трём сторонам."""
        if abs(a - b) < eps and abs(b - c) < eps:
            return "равносторонний"
        if abs(a - b) < eps or abs(b - c) < eps or abs(a - c) < eps:
            return "равнобедренный"
        return "разносторонний"
