from unittest.mock import MagicMock

import pytest
import scrapy

from scrapy_wayback_middleware import WaybackMiddleware


@pytest.fixture(autouse=True)
def scrapy_request(monkeypatch):
    monkeypatch.setattr(scrapy, "Request", MagicMock())


def test_process_spider_output():
    middleware = WaybackMiddleware()
    response_mock = MagicMock()
    response_mock.url = "https://example.com"
    [res for res in middleware.process_spider_output(response_mock, [], None)]
    scrapy.Request.assert_called_once()


def test_ignore_archive_urls():
    middleware = WaybackMiddleware()
    response_mock = MagicMock()
    response_mock.url = "https://web.archive.org/save/https://example.com"
    [res for res in middleware.process_spider_output(response_mock, [], None)]
    scrapy.Request.assert_not_called()


def test_get_item_urls(monkeypatch, scrapy_request):
    middleware = WaybackMiddleware()
    monkeypatch.setattr(
        middleware, "get_item_urls", lambda x: ["https://example.com/test"]
    )
    response_mock = MagicMock()
    response_mock.url = "https://example.com"
    [res for res in middleware.process_spider_output(response_mock, [None], None)]
    assert len(scrapy.Request.mock_calls) == 2
