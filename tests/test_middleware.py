from unittest.mock import MagicMock, Mock

import pytest
import scrapy

from scrapy_wayback_middleware import WaybackMiddleware
from scrapy_wayback_middleware.middleware import SLOT_KEY


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
    assert scrapy.Request.call_args[1]["meta"]["download_slot"] == SLOT_KEY


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
    middleware = WaybackMiddleware(MagicMock(), is_post=True)
    [res for res in middleware.process_spider_output(response_mock, [], None)]
    scrapy.Request.assert_called_once()
    assert scrapy.Request.call_args[0][0] == "https://pragma.archivelab.org"
    assert scrapy.Request.call_args[1]["meta"]["download_slot"] == SLOT_KEY


def test_ignore_post_requests(scrapy_request, response_mock):
    middleware = WaybackMiddleware(MagicMock())
    response_mock.request.method = "POST"
    [res for res in middleware.process_spider_output(response_mock, [], None)]
    scrapy.Request.assert_not_called()


def test_set_slot_delay_on_429(response_mock):
    response_mock.status = 429
    request_mock = MagicMock()
    request_mock.meta = {"download_slot": SLOT_KEY}
    crawler_mock = MagicMock()
    slot_mock = Mock()
    slot_mock.delay = 0
    crawler_mock.engine.downloader.slots.get.return_value = slot_mock
    middleware = WaybackMiddleware(crawler_mock)
    middleware._response_downloaded(response_mock, request_mock, None)

    crawler_mock.engine.downloader.slots.get.assert_called_once()
    assert middleware.delay_seconds > 0
    assert slot_mock.delay > 0


def test_reset_slot_delay(monkeypatch, response_mock):
    conc_delay_mock = MagicMock()
    conc_delay_mock.return_value = 0, 1
    monkeypatch.setattr(
        "scrapy_wayback_middleware.middleware._get_concurrency_delay", conc_delay_mock
    )
    request_mock = MagicMock()
    request_mock.meta = {"download_slot": SLOT_KEY}
    crawler_mock = MagicMock()
    slot_mock = Mock()
    slot_mock.delay = 10
    crawler_mock.engine.downloader.slots.get.return_value = slot_mock
    middleware = WaybackMiddleware(crawler_mock)
    middleware._response_downloaded(response_mock, request_mock, None)

    crawler_mock.engine.downloader.slots.get.assert_called_once()
    assert slot_mock.delay == 1
