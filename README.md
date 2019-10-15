# Scrapy Wayback Middleware

[![Build status](https://github.com/City-Bureau/scrapy-wayback-middleware/workflows/CI/badge.svg)](https://github.com/City-Bureau/scrapy-wayback-middleware/actions)

Middleware for submitting all scraped response URLs to the [Internet Archive Wayback Machine](https://archive.org/web/) for archival.

## Installation

```bash
pip install scrapy-wayback-middleware
```

## Setup

Add `scrapy_wayback_middleware.WaybackMiddleware` to your project's `SPIDER_MIDDLEWARES` settings. By default, the middleware will make `GET` requests to `web.archive.org/save/{URL}`, but if the `WAYBACK_MIDDLEWARE_POST` setting is `True` then it will make POST requests to [`pragma.archivelab.org`](https://archive.readme.io/docs/creating-a-snapshot) instead.

## Configuration

To configure custom behavior for certain methods, subclass `WaybackMiddleware` and override the `get_item_urls` method to pull additional links to archive from individual items or `handle_wayback` to change how responses from the Wayback Machine are handled. The `WAYBACK_MIDDLEWARE_POST` can be set to `True` to adjust request behavior.

### Duplicate Filtering

In order to avoid sending duplicate requests with `WAYBACK_MIDDLEWARE_POST` set to `False`, you'll need to either include `web.archive.org` in your spider's `allowed_domains` property (if specified) or disable `scrapy.spidermiddlewares.offsite.OffsiteMiddleware` in your settings.

### Rate Limits

While neither endpoint returns headers indicating specific rate limits, the `GET` endpoint at `web.archive.org/save` has a rate limit of 25 requests/minute, resetting each minute. The middleware is configured to wait for 60 seconds whenever it sees a 429 error code to handle this.
