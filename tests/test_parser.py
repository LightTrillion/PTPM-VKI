"""Юнит-тесты парсера ForumParser.

Сеть не используется: HTML берётся из сохранённого слепка (фикстуры),
а HTTP-вызов подменяется заглушкой. Тесты детерминированы и работают офлайн.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests

from src.parser import ForumParser
from src.database import DatabaseRepository

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "sample_forum.html"


class TestForumParser(unittest.TestCase):

    def setUp(self):
        """Читаем HTML-слепок один раз перед каждым тестом."""
        self.html = FIXTURE.read_text(encoding="utf-8")
        self.parser = ForumParser()

    # --- parse_html: чистая логика, без сети ---

    def test_parse_html_extracts_all_valid_comments(self):
        """Из фикстуры извлекаются id, логин и текст с сохранением HTML-разметки."""
        data = self.parser.parse_html(self.html)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], {"id": 101, "name": "alice",
                                   "message": "<p>Hello <b>world</b></p>"})
        self.assertEqual(data[1], {"id": 102, "name": "bob",
                                   "message": "Second comment"})

    def test_parse_html_skips_non_numeric_id(self):
        """Блок с data-id='not-an-int' пропускается, парсер не падает."""
        data = self.parser.parse_html(self.html)
        self.assertEqual([item["id"] for item in data], [101, 102])

    def test_parse_html_empty_page_returns_empty_list(self):
        """На странице без комментариев возвращается пустой список."""
        self.assertEqual(self.parser.parse_html("<html><body></body></html>"), [])

    # --- parse_page / fetch_page: HTTP подменён заглушкой ---

    def test_parse_page_requests_url_with_timeout_and_parses(self):
        """parse_page скачивает страницу по URL с таймаутом и парсит ответ."""
        response = Mock()
        response.text = self.html
        with patch.object(self.parser.session, "get", return_value=response) as mock_get:
            data = self.parser.parse_page("https://example.org/topic")
        mock_get.assert_called_once_with("https://example.org/topic", timeout=10)
        response.raise_for_status.assert_called_once()
        self.assertEqual(len(data), 2)

    def test_fetch_page_raises_on_http_error(self):
        """HTTP 404 приводит к requests.HTTPError (raise_for_status)."""
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        with patch.object(self.parser.session, "get", return_value=response):
            with self.assertRaises(requests.HTTPError):
                self.parser.fetch_page("https://example.org/missing")

    # --- save_to_db: и с реальной БД, и с моком репозитория ---

    def test_save_to_db_inserts_new_and_updates_existing(self):
        """Первый обход добавляет записи, повторный — обновляет message (upsert)."""
        repo = DatabaseRepository(":memory:")
        try:
            data = self.parser.parse_html(self.html)
            self.assertEqual(self.parser.save_to_db(data, repo), 2)

            changed = [{"id": 101, "name": "alice", "message": "edited"}]
            self.assertEqual(self.parser.save_to_db(changed, repo), 1)
            self.assertEqual(repo.get_by_id(101)["message"], "edited")
            self.assertEqual(len(repo.get_by_name("alice")), 1)  # дубль не появился
        finally:
            repo.close()

    def test_save_to_db_calls_repository_add_for_new_item(self):
        """Для нового id вызывается add, а update не вызывается."""
        repo = Mock()
        repo.get_by_id.return_value = None
        count = self.parser.save_to_db([{"id": 7, "name": "u", "message": "m"}], repo)
        self.assertEqual(count, 1)
        repo.add.assert_called_once_with(7, "u", "m")
        repo.update.assert_not_called()


if __name__ == "__main__":
    unittest.main()