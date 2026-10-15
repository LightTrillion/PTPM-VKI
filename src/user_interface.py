"""Класс взаимодействия с пользователем: абстрактный интерфейс + консольная реализация."""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class UserInterface(ABC):
    """
    Абстрактный базовый класс — интерфейс взаимодействия с пользователем.
    Реализации должны предоставить методы для ввода и вывода данных.
    """

    @abstractmethod
    def get_triangle_sides(self) -> tuple:
        """
        Запрашивает у пользователя три стороны треугольника.

        Returns:
            tuple из трёх значений (сторона A, сторона B, сторона C)
        """
        pass

    @abstractmethod
    def show_result(self, result: dict) -> None:
        """
        Отображает результат пользователю.

        Args:
            result: dict с ключами "type", "error", "vertices"
        """
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        """Отображает сообщение об ошибке."""
        pass


class ConsoleUI(UserInterface):
    """
    Консольная реализация интерфейса пользователя.
    Ввод данных через функцию input(), вывод через print().
    """

    def get_triangle_sides(self) -> tuple:
        """Запрашивает три стороны треугольника через консоль."""
        print("\n=== Определение типа треугольника ===")
        a = input("Введите длину стороны A: ")
        b = input("Введите длину стороны B: ")
        c = input("Введите длину стороны C: ")
        logger.debug("Пользователь ввёл: %s, %s, %s", a, b, c)
        return a, b, c

    def show_result(self, result: dict) -> None:
        """Выводит результат в консоль."""
        tri_type = result.get("type", "")
        error = result.get("error")
        if error:
            print(f"Ошибка: {error}")
        if tri_type:
            print(f"Тип треугольника: {tri_type}")
        elif tri_type == "":
            print("Тип не определён (некорректные данные)")
        vertices = result.get("vertices")
        if vertices:
            print(f"Вершины: {vertices}")

    def show_error(self, message: str) -> None:
        """Выводит сообщение об ошибке в консоль."""
        print(f"Ошибка: {message}")
