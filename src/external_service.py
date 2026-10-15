"""Класс сторонней зависимости: абстрактный интерфейс + имитация отправки на email-сервер."""

from abc import ABC, abstractmethod
import logging
import time

logger = logging.getLogger(__name__)


class ExternalService(ABC):
    """
    Абстрактный базовый класс — интерфейс сторонней зависимости.
    Используется для имитации отправки данных стороннему процессу (например, email-серверу).
    """

    @abstractmethod
    def send(self, message: str) -> bool:
        """
        Отправляет сообщение стороннему сервису.

        Args:
            message: строка для отправки

        Returns:
            True если отправка успешна, False в противном случае
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Возвращает статус сервиса."""
        pass


class EmailService(ExternalService):
    """
    Реализация сторонней зависимости — имитация отправки на email-сервер.

    Внутри реализуется исключительно имитация передачи данных:
    вместо реальной отправки сообщение логируется.
    """

    def __init__(self, server_address: str = "smtp.example.com", port: int = 587):
        """
        Args:
            server_address: адрес SMTP-сервера (для имитации)
            port: порт SMTP-сервера (для имитации)
        """
        self.server_address = server_address
        self.port = port
        self._connected = False
        self._sent_messages = []
        logger.info(
            "EmailService создан: сервер=%s, порт=%d", server_address, port
        )

    def connect(self) -> bool:
        """Имитация подключения к SMTP-серверу."""
        self._connected = True
        logger.info("Подключён к SMTP-серверу %s:%d", self.server_address, self.port)
        return True

    def disconnect(self) -> bool:
        """Имитация отключения от SMTP-сервера."""
        self._connected = False
        logger.info("Отключён от SMTP-сервера")
        return True

    def send(self, message: str) -> bool:
        """
        Имитация отправки сообщения на email-сервер.

        Returns:
            True если отправка (имитация) успешна
        """
        if not self._connected:
            logger.warning("EmailService не подключён. Подключаемся автоматически.")
            self.connect()

        try:
            # Имитация сетевой задержки
            time.sleep(0.01)

            # Имитация отправки: сохраняем сообщение
            self._sent_messages.append(message)
            logger.info(
                "[ИМИТАЦИЯ] Сообщение отправлено на %s:%d: %s",
                self.server_address, self.port, message,
            )
            return True
        except Exception as e:
            logger.error("Ошибка при отправке: %s", e)
            return False

    def get_status(self) -> str:
        """Возвращает статус подключения к серверу."""
        return "connected" if self._connected else "disconnected"

    def get_sent_messages(self) -> list:
        """Возвращает список всех отправленных сообщений (для тестирования)."""
        return list(self._sent_messages)
