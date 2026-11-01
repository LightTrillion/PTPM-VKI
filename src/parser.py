from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup


class ForumParser:
    """
    Парсер форума или другой структурированной HTML-страницы.

    По умолчанию используется простая тестовая разметка:

    <article class="comment" data-id="123">
        <div class="author">username</div>
        <div class="message">message html</div>
    </article>

    Для реального сайта можно передать другие CSS-селекторы в конструктор.
    """

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ru,en;q=0.9",
    }

    def __init__(
        self,
        article_selector: str = "article.comment",
        id_attribute: str = "data-id",
        author_selector: str = ".author",
        message_selector: str = ".message",
        headers: Dict[str, str] | None = None,
    ) -> None:
        """
        Создаёт парсер.

        :param article_selector: CSS-селектор одного комментария.
        :param id_attribute: атрибут, в котором хранится ID комментария.
        :param author_selector: CSS-селектор имени автора.
        :param message_selector: CSS-селектор текста сообщения.
        :param headers: дополнительные HTTP-заголовки.
        """
        self.article_selector = article_selector
        self.id_attribute = id_attribute
        self.author_selector = author_selector
        self.message_selector = message_selector

        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

        if headers:
            self.session.headers.update(headers)

    def fetch_page(self, url: str) -> str:
        """
        Скачивает HTML-страницу по URL.

        :param url: адрес страницы.
        :return: HTML-код страницы.
        """
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def parse_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Скачивает страницу и парсит комментарии.

        :param url: адрес страницы.
        :return: список словарей с комментариями.
        """
        html = self.fetch_page(url)
        return self.parse_html(html)

    def parse_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Парсит HTML-код и возвращает список комментариев.

        :param html: HTML-код страницы.
        :return: список словарей вида {"id": ..., "name": ..., "message": ...}.
        """
        soup = BeautifulSoup(html, "lxml")
        comments: List[Dict[str, Any]] = []

        for node in soup.select(self.article_selector):
            raw_id = node.get(self.id_attribute)

            if raw_id is None:
                continue

            try:
                comment_id = int(raw_id)
            except (TypeError, ValueError):
                continue

            author_node = node.select_one(self.author_selector)
            message_node = node.select_one(self.message_selector)

            if author_node is None or message_node is None:
                continue

            name = author_node.get_text(strip=True)
            message = message_node.decode_contents().strip()

            comments.append(
                {
                    "id": comment_id,
                    "name": name,
                    "message": message,
                }
            )

        return comments

    def save_to_db(self, parsed_data: List[Dict[str, Any]], repository) -> int:
        """
        Сохраняет распаршенные комментарии в базу данных через репозиторий.

        Если комментарий с таким ID уже существует, обновляется его message.

        :param parsed_data: список распаршенных комментариев.
        :param repository: объект DatabaseRepository.
        :return: количество обработанных записей.
        """
        saved_count = 0

        for item in parsed_data:
            comment_id = item.get("id")
            name = item.get("name")
            message = item.get("message")

            if comment_id is None or name is None or message is None:
                continue

            existing = repository.get_by_id(comment_id)

            if existing is None:
                repository.add(comment_id, name, message)
            else:
                repository.update(comment_id, message)

            saved_count += 1

        return saved_count