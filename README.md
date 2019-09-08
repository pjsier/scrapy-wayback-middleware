# Scrapy Wayback Middleware

[![Build Status](https://travis-ci.org/City-Bureau/scrapy-wayback-middleware.svg?branch=master)](https://travis-ci.org/City-Bureau/scrapy-wayback-middleware)

Middleware for submitting all scraped response URLs to the [Internet Archive Wayback Machine](https://archive.org/web/) for archival.

## Installation

```bash
pip install scrapy-wayback-middleware
```

## Setup

Add `scrapy_wayback_middleware.WaybackMiddleware` to your project's `SPIDER_MIDDLEWARES` settings. By default, the middleware will make GET requests to `web.archive.org/save/{URL}`, but if the `WAYBACK_MIDDLEWARE_POST` setting is `True` then it will make POST requests to [`pragma.archivelab.org`](https://archive.readme.io/docs/creating-a-snapshot) instead.

### Configuration

To configure custom behavior for certain methods, subclass `WaybackMiddleware` and override the `get_item_urls` method to pull additional links to archive from individual items or `handle_wayback` to change how responses from the Wayback Machine are handled. The `WAYBACK_MIDDLEWARE_POST` can be set to `True` to adjust request behavior.
