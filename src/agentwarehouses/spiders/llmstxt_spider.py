from __future__ import annotations

import re
from collections.abc import Generator
from datetime import datetime, timezone
from typing import Any

import scrapy
from rbloom import Bloom
from scrapy.http import Response
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError
from twisted.python.failure import Failure

from agentwarehouses.items import DocPageItem


class LlmstxtSpider(scrapy.Spider):
    """Crawl every documentation page listed in llms.txt.

    The spider fetches the llms.txt index, extracts all .md page URLs,
    deduplicates them with a rbloom Bloom filter, and downloads each
    markdown page to extract title, description, and body content.

    Usage:
        scrapy crawl llmstxt
        scrapy crawl llmstxt -a index_url=https://example.com/llms.txt
    """

    name = "llmstxt"
    allowed_domains = ["code.claude.com"]

    custom_settings: dict[bool | float | int | str | None, Any] | None = {
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "DOWNLOAD_DELAY": 0.25,
    }

    def __init__(self, index_url: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.index_url: str = index_url or "https://code.claude.com/docs/llms.txt"
        self.start_urls: list[str] = [self.index_url]
        # Bloom filter: expect up to 500 URLs, false-positive rate 0.01%
        self.seen: Bloom = Bloom(500, 0.0001)
        self._stats: dict[str, int] = {"index_urls": 0, "pages_fetched": 0, "pages_failed": 0}

    def parse(self, response: Response) -> Generator[scrapy.Request, None, None]:
        """Parse the llms.txt index and yield requests for each doc page."""
        text: str = response.text
        urls: list[str] = re.findall(r"https://code\.claude\.com/docs/en/[\w./-]+\.md", text)
        self._stats["index_urls"] = len(urls)
        self.logger.info("Found %d documentation URLs in llms.txt", len(urls))

        for url in urls:
            if url not in self.seen:
                self.seen.add(url)
                yield scrapy.Request(
                    url,
                    callback=self.parse_doc_page,
                    errback=self.handle_error,
                )

    def parse_doc_page(self, response: Response) -> Generator[DocPageItem, None, None]:
        """Extract content from a fetched markdown documentation page."""
        self._stats["pages_fetched"] += 1
        text: str = response.text

        title: str = self._extract_title(text)
        description: str = self._extract_description(text)
        headings: list[dict[str, Any]] = self._extract_headings(text)

        item = DocPageItem()
        item["url"] = response.url
        item["title"] = title
        item["description"] = description
        item["headings"] = headings
        item["body_markdown"] = text
        item["content_length"] = len(text)
        item["crawled_at"] = datetime.now(timezone.utc).isoformat()

        yield item

    def handle_error(self, failure: Failure) -> None:
        """Log errors without crashing the crawl."""
        self._stats["pages_failed"] += 1
        request: scrapy.Request = failure.request  # type: ignore[attr-defined]
        url: str = request.url

        if failure.check(HttpError):  # type: ignore[no-untyped-call]
            exc = failure.value
            assert exc is not None
            status: int = exc.response.status  # type: ignore[attr-defined]
            self.logger.error("ERROR: HTTP %d fetching %s", status, url)
        elif failure.check(DNSLookupError):  # type: ignore[no-untyped-call]
            self.logger.error("ERROR: DNS lookup failed for %s", url)
        elif failure.check(TimeoutError):  # type: ignore[no-untyped-call]
            self.logger.error("ERROR: Timeout fetching %s", url)
        else:
            failure_type = failure.type
            type_name = failure_type.__name__ if failure_type is not None else "Unknown"
            self.logger.error("ERROR: %s fetching %s", type_name, url)

    def closed(self, reason: str) -> None:
        """Log crawl summary stats on spider close."""
        self.logger.info(
            "Crawl complete: index_urls=%d fetched=%d failed=%d reason=%s",
            self._stats["index_urls"],
            self._stats["pages_fetched"],
            self._stats["pages_failed"],
            reason,
        )

    @staticmethod
    def _extract_title(text: str) -> str:
        """Extract title from first H1 heading."""
        match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_description(text: str) -> str:
        """Extract description from first blockquote."""
        match = re.search(r"^>\s*(.+)$", text, re.MULTILINE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_headings(text: str) -> list[dict[str, Any]]:
        """Extract all headings as a list of (level, text) for structure analysis."""
        return [
            {"level": len(m.group(1)), "text": m.group(2).strip()}
            for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)
        ]
