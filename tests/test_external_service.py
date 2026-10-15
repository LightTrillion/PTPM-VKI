"""Юнит-тесты для классов ExternalService и EmailService."""

import unittest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from external_service import ExternalService, EmailService


class TestExternalService(unittest.TestCase):
    """Тесты абстрактного класса и EmailService."""

    def test_cannot_instantiate_abstract_class(self):
        """Нельзя создать экземпляр абстрактного класса."""
        with self.assertRaises(TypeError):
            ExternalService()

    def test_email_service_send_returns_true(self):
        """EmailService.send возвращает True при успешной имитации отправки."""
        service = EmailService()
        service.connect()
        result = service.send("Тестовое сообщение")
        self.assertTrue(result)

    def test_email_service_stores_sent_messages(self):
        """EmailService сохраняет отправленные сообщения."""
        service = EmailService()
        service.connect()
        service.send("Сообщение 1")
        service.send("Сообщение 2")
        messages = service.get_sent_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0], "Сообщение 1")
        self.assertEqual(messages[1], "Сообщение 2")

    def test_email_service_status_connected(self):
        """Статус подключения возвращает 'connected' после connect()."""
        service = EmailService()
        self.assertEqual(service.get_status(), "disconnected")
        service.connect()
        self.assertEqual(service.get_status(), "connected")

    def test_email_service_status_disconnected(self):
        """Статус подключения возвращает 'disconnected' после disconnect()."""
        service = EmailService()
        service.connect()
        service.disconnect()
        self.assertEqual(service.get_status(), "disconnected")

    def test_email_service_auto_connects_on_send(self):
        """EmailService автоматически подключается при send(), если не подключён."""
        service = EmailService()
        self.assertEqual(service.get_status(), "disconnected")
        result = service.send("Тест")
        self.assertTrue(result)
        self.assertEqual(service.get_status(), "connected")


if __name__ == "__main__":
    unittest.main()
