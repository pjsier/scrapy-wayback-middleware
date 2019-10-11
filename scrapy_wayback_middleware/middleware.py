import json
import time

import scrapy


class WaybackMiddleware:
    """Middleware for submitting URLs to the Internet Archive Wayback Machine"""

    @classmethod
    def from_crawler(cls, crawler):
        is_post = crawler.settings.get("WAYBACK_MIDDLEWARE_POST")
        return cls(crawler, is_post=(is_post and is_post is not None))

    def __init__(self, crawler, is_post=False):
        self.crawler = crawler
        self.is_post = is_post

    def process_spider_input(self, response, spider):
        if response.status == 429:
            self.crawler.engine.pause()
            time.sleep(60)
            self.crawler.engine.unpause()

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
                    },
                )

    def handle_wayback(self, response):
        """Override for custom processing of Wayback Machine response"""
        pass

    def get_item_urls(self, item):
        """Returns iterable. Override to pull URLs from returned items"""
        return []
