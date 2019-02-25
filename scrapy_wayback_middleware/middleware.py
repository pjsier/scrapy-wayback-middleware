import scrapy


class WaybackMiddleware:
    """Middleware for submitting URLs to the Internet Archive Wayback Machine"""

    def process_spider_output(self, response, result, spider):
        """Process normally, adding Wayback Machine requests"""
        wayback_urls = [response.url]
        for item in result:
            wayback_urls.extend([item_url for item_url in self.get_item_urls(item)])
            yield item
        for wayback_url in wayback_urls:
            if "web.archive.org" in wayback_url:
                continue
            yield scrapy.Request(
                "https://web.archive.org/save/{}".format(wayback_url),
                callback=self.handle_wayback,
                meta={"dont_obey_robotstxt": True, "dont_redirect": True},
                dont_filter=True,
            )

    def handle_wayback(self, response):
        """Override for custom processing of Wayback Machine response"""
        pass

    def get_item_urls(self, item):
        """Returns iterable. Override to pull URLs from returned items"""
        return []
