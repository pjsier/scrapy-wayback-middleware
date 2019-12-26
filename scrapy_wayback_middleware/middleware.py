import json
from datetime import datetime, timedelta

import scrapy
from scrapy import signals
from scrapy.core.downloader import _get_concurrency_delay

SLOT_KEY = "_wayback_slot"


class WaybackMiddleware:
    """Middleware for submitting URLs to the Internet Archive Wayback Machine"""

    @classmethod
    def from_crawler(cls, crawler):
        is_post = crawler.settings.get("WAYBACK_MIDDLEWARE_POST")
        return cls(crawler, is_post=(is_post and is_post is not None))

    def __init__(self, crawler, is_post=False):
        self.crawler = crawler
        self.is_post = is_post
        self.delay_until = datetime.now()
        self.crawler.signals.connect(
            self._response_downloaded, signal=signals.response_downloaded
        )

    @property
    def delay_seconds(self):
        """Calculate delay in seconds if a delay is set, otherwise return 0"""
        current_time = datetime.now()
        if current_time < self.delay_until:
            return (self.delay_until - datetime.now()).seconds
        return 0

    def _response_downloaded(self, response, request, spider):
        """
        Adjust Wayback Machine slot download delay if 429 response codes are returned.

        Based on the AutoThrottle extension.
        """
        key = request.meta.get("download_slot")
        if key != SLOT_KEY:
            return
        slot = self.crawler.engine.downloader.slots.get(SLOT_KEY)

        # Get default values for concurrency and delay
        ip_concurrency = self.crawler.settings.getint("CONCURRENT_REQUESTS_PER_IP")
        domain_concurrency = self.crawler.settings.getint(
            "CONCURRENT_REQUESTS_PER_DOMAIN"
        )
        _conc, delay = _get_concurrency_delay(
            ip_concurrency if ip_concurrency else domain_concurrency,
            spider,
            self.crawler.settings,
        )

        if response.status == 429:
            # Update the delay datetime if the response has a 429 status code
            self.delay_until = datetime.now() + timedelta(seconds=60)
            slot.delay = self.delay_seconds
        elif self.delay_seconds < delay and slot.delay > delay:
            # If the status code is not 429 and the delay is passed, reset slot delay
            slot.delay = delay

    def process_spider_output(self, response, result, spider):
        """Process normally, adding Wayback Machine requests"""
        wayback_urls = []
        if response.request.method == "GET":
            wayback_urls.append(response.url)
        for item in result:
            wayback_urls.extend([item_url for item_url in self.get_item_urls(item)])
            yield item
        for wayback_url in wayback_urls:
            if "web.archive.org" in wayback_url:
                continue
            if self.is_post:
                yield scrapy.Request(
                    "https://pragma.archivelab.org",
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({"url": wayback_url}),
                    callback=self.handle_wayback,
                    meta={
                        "handle_httpstatus_list": [200, 429],
                        "dont_obey_robotstxt": True,
                        "dont_redirect": True,
                        "dont_retry": True,
                        "download_slot": SLOT_KEY,
                    },
                    dont_filter=True,
                )
            else:
                yield scrapy.Request(
                    "https://web.archive.org/save/{}".format(wayback_url),
                    callback=self.handle_wayback,
                    meta={
                        "handle_httpstatus_list": [200, 429],
                        "dont_obey_robotstxt": True,
                        "dont_redirect": True,
                        "dont_retry": True,
                        "download_slot": SLOT_KEY,
                    },
                )

    def handle_wayback(self, response):
        """Override for custom processing of Wayback Machine response"""
        pass

    def get_item_urls(self, item):
        """Returns iterable. Override to pull URLs from returned items"""
        return []
