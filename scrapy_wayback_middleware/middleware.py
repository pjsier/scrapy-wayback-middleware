import json

import scrapy


class WaybackMiddleware:
    """Middleware for submitting URLs to the Internet Archive Wayback Machine"""

    @classmethod
    def from_crawler(cls, crawler):
        is_post = crawler.settings.get("WAYBACK_MIDDLEWARE_POST")
        return cls(is_post=(is_post and is_post is not None))

    def __init__(self, is_post=False):
        self.is_post = is_post

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
                    meta={"dont_obey_robotstxt": True, "dont_redirect": True},
                    dont_filter=True,
                )
            else:
                yield scrapy.Request(
                    "https://web.archive.org/save/{}".format(wayback_url),
                    callback=self.handle_wayback,
                    meta={"dont_obey_robotstxt": True, "dont_redirect": True},
                )

    def handle_wayback(self, response):
        """Override for custom processing of Wayback Machine response"""
        pass

    def get_item_urls(self, item):
        """Returns iterable. Override to pull URLs from returned items"""
        return []
