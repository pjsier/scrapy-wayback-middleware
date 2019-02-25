# Scrapy Wayback Middleware

Middleware for submitting all scraped response URLs to the [Internet Archive Wayback Machine](https://archive.org/web/) for archival.

## Installation

```bash
pip install scrapy-wayback-middleware
```

## Setup

Add `scrapy_wayback_middleware.WaybackMiddleware` to your project's `SPIDER_MIDDLEWARES` settings.

### Configuration

To configure custom behavior for certain methods, subclass `WaybackMiddleware` and override the `get_item_urls` method to pull additional links to archive from individual items or `handle_wayback` to change how responses from the Wayback Machine are handled.
