from unittest.mock import MagicMock

import pytest
import scrapy

from scrapy_wayback_middleware import WaybackMiddleware


@pytest.fixture(autouse=True)
def scrapy_request(monkeypatch):
    monkeypatch.setattr(scrapy, "Request", MagicMock())


@pytest.fixture
def response_mock():
    res_mock = MagicMock()
    res_mock.url = "https://example.com"
    res_mock.request.method = "GET"
    return res_mock


def test_process_spider_output(response_mock):
    middleware = WaybackMiddleware(MagicMock())
    [res for res in middleware.process_spider_output(response_mock, [], None)]
    scrapy.Request.assert_called_once()
    assert (
        scrapy.Request.call_args[0][0]
        == "https://web.archive.org/save/https://example.com"
    )


def test_ignore_archive_urls(response_mock):
    middleware = WaybackMiddleware(MagicMock())
    response_mock.url = "https://web.archive.org/save/https://example.com"
    [res for res in middleware.process_spider_output(response_mock, [], None)]
    scrapy.Request.assert_not_called()


def test_get_item_urls(monkeypatch, scrapy_request, response_mock):
    middleware = WaybackMiddleware(MagicMock())
    monkeypatch.setattr(
        middleware, "get_item_urls", lambda x: ["https://example.com/test"]
    )
    [res for res in middleware.process_spider_output(response_mock, [None], None)]
    assert len(scrapy.Request.mock_calls) == 2


def test_use_post_request(response_mock):
    middleware = WaybackMiddleware(MagicMock, is_post=True)
    [res for res in middleware.process_spider_output(response_mock, [], None)]
    scrapy.Request.assert_called_once()
    assert scrapy.Request.call_args[0][0] == "https://pragma.archivelab.org"


def test_ignore_post_requests(scrapy_request, response_mock):
    middleware = WaybackMiddleware(MagicMock())
    response_mock.request.method = "POST"
    [res for res in middleware.process_spider_output(response_mock, [], None)]
    scrapy.Request.assert_not_called()


def test_pause_on_429(response_mock):
    response_mock.status = 429
    crawler_mock = MagicMock()
    crawler_mock.engine = MagicMock()
    middleware = WaybackMiddleware(crawler_mock)
    middleware.process_spider_input(response_mock, None)
    crawler_mock.engine.pause.assert_called_once()
