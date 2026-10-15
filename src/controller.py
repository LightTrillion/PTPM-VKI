"""Класс-контроллер: бизнес-логика сквозного сценария."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Controller:
    """
    Класс-контроллер, реализующий бизнес-логику сквозного сценария:

    1. Запрашивает входные данные у пользователя (через UserInterface).
    2. Проверяет наличие записи в БД:
       - Если записи нет → вычисляет результат (TriangleCalculator)
         и добавляет запись в БД.
       - Если запись есть → берёт результат из БД.
    3. Отправляет строку-результат сторонней зависимости (ExternalService).
    4. Возвращает результат выполнения операции.
    """

    def __init__(
        self,
        calculator,
        database,
        user_interface,
        external_service,
    ):
        """
        Args:
            calculator: экземпляр TriangleCalculator
            database: экземпляр TriangleDatabase
            user_interface: экземпляр UserInterface
            external_service: экземпляр ExternalService
        """
        self.calculator = calculator
        self.database = database
        self.ui = user_interface
        self.external_service = external_service
        logger.info("Контроллер инициализирован")

    def run(self) -> dict:
        """
        Выполняет сквозной сценарий.

        Returns:
            dict с результатом: {"type", "error", "vertices", "source"}
            где source = "database" или "calculated"
        """
        logger.info("=== Начало выполнения сценария ===")

        # Шаг 1: Получаем данные от пользователя
        a, b, c = self.ui.get_triangle_sides()
        logger.debug("Получены стороны: %s, %s, %s", a, b, c)

        # Шаг 2: Проверяем наличие записи в БД
        db_record = self._get_record_from_db(a, b, c)

        if db_record is not None:
            # Запись найдена — берём результат из БД
            logger.info("Результат найден в БД")
            result = {
                "type": db_record["triangle_type"],
                "error": db_record["error_message"],
                "vertices": None,
                "source": "database",
            }
        else:
            # Записи нет — вычисляем результат
            logger.info("Запись не найдена в БД, выполняем вычисление")
            calc_result = self.calculator.calculate(a, b, c)

            # Добавляем запись в БД
            fa, fb, fc = self._parse_sides(a, b, c)
            if fa is not None:
                self.database.add_record(
                    fa, fb, fc,
                    calc_result["type"],
                    calc_result["error"],
                )

            result = {
                "type": calc_result["type"],
                "error": calc_result["error"],
                "vertices": calc_result.get("vertices"),
                "source": "calculated",
            }

        # Шаг 3: Отправляем результат сторонней зависимости
        message = self._format_message(result)
        sent = self.external_service.send(message)
        if not sent:
            logger.warning("Не удалось отправить результат сторонней зависимости")
        result["sent"] = sent

        # Шаг 4: Отображаем результат пользователю
        self.ui.show_result(result)

        logger.info("=== Сценарий завершён ===")
        return result

    def _get_record_from_db(self, a, b, c) -> Optional[dict]:
        """
        Получает запись из БД, преобразуя стороны в float.
        Если стороны нечисловые — возвращает None.
        """
        fa, fb, fc = self._parse_sides(a, b, c)
        if fa is None:
            return None
        return self.database.get_record(fa, fb, fc)

    @staticmethod
    def _parse_sides(a, b, c) -> tuple:
        """Пытается преобразовать стороны в float. Возвращает (None, None, None) при ошибке."""
        try:
            fa = float(str(a).strip())
            fb = float(str(b).strip())
            fc = float(str(c).strip())
            return fa, fb, fc
        except (ValueError, TypeError):
            return None, None, None

    @staticmethod
    def _format_message(result: dict) -> str:
        """Формирует строку-результат для отправки сторонней зависимости."""
        tri_type = result.get("type", "")
        error = result.get("error")
        if error:
            return f"Ошибка: {error}"
        if tri_type == "не треугольник":
            return "Не треугольник"
        return f"Тип треугольника: {tri_type}"
