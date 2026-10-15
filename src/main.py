"""Точка входа: сборка и запуск приложения."""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from triangle_calculator import TriangleCalculator
from database import TriangleDatabase
from user_interface import ConsoleUI
from external_service import EmailService
from controller import Controller


def setup_logging():
    """Настройка логгера."""
    log_dir = "Logs"
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | [%(levelname)-7s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                os.path.join(log_dir, "lab3.log"), encoding="utf-8"
            ),
        ],
    )


def main():
    """Сборка всех компонентов и запуск сценария."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Приложение запущено")

    # Создаём компоненты
    calculator = TriangleCalculator()
    database = TriangleDatabase(db_path="triangles.db")
    ui = ConsoleUI()
    email_service = EmailService()
    email_service.connect()

    # Собираем контроллер
    controller = Controller(
        calculator=calculator,
        database=database,
        user_interface=ui,
        external_service=email_service,
    )

    try:
        controller.run()
    finally:
        email_service.disconnect()
        database.close()

    logger.info("Приложение завершено")


if __name__ == "__main__":
    main()
