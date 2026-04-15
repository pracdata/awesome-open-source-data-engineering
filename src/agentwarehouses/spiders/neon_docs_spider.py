"""Neon docs discovery spider — crawls llms.txt, sitemap, and guide pages.

Discovers all Neon documentation pages from four sources:
  1. neon.com/llms.txt          — AI-curated doc index
  2. neon.com/sitemap-0.xml     — full doc sitemap (1,087 URLs)
  3. neon.com/blog-sitemap.xml  — blog posts (300+ URLs)
  4. neon.com/sitemap-postgres.xml — PG tutorial/reference (846 URLs)

Uses rbloom Bloom filter for O(1) URL deduplication across all sources.
Follows links from llms.txt entries to fetch full page content.

Usage:
    scrapy crawl neon_docs
    scrapy crawl neon_docs -a max_pages=50
    scrapy crawl neon_docs -a sources=llms,sitemap
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Generator
from datetime import datetime, timezone
from typing import Any

import scrapy
from rbloom import Bloom
from scrapy.http import Response
from twisted.python.failure import Failure

from agentwarehouses.items import DocPageItem

# llms.txt link pattern: - [Title](URL): description
LLMS_ENTRY_RE = re.compile(r"- \[([^\]]+)\]\(([^)]+)\)(?::\s*(.+))?")

# Sitemap <loc> extraction
SITEMAP_LOC_RE = re.compile(r"<loc>([^<]+)</loc>")

# Language filter: skip non-English docs
LANG_FILTER_RE = re.compile(r"/(?:ja-jp|de-de|fr-fr|ko-kr|zh-cn|pt-br|es-es)/")

# Guide URL pattern from sitemap
GUIDE_PATH_RE = re.compile(r"^https://neon\.com/docs/guides/")

# All Neon doc patterns
DOC_PATH_RE = re.compile(r"^https://neon\.com/(?:docs|branching|postgresql|guides)/")


class NeonDocsSpider(scrapy.Spider):
    """Multi-source Neon documentation crawler with rbloom dedup.

    Crawls llms.txt, sitemaps, and follows guide links. Deduplicates
    URLs across all sources using a Bloom filter (5,000 capacity, 0.01% FP).
    """

    name = "neon_docs"

    custom_settings: dict[str, Any] = {
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "DOWNLOAD_DELAY": 0.5,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 2.0,
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_TIMEOUT": 30,
        "RETRY_TIMES": 3,
    }

    # Discovery endpoints
    SOURCES = {
        "llms": "https://neon.com/llms.txt",
        "sitemap": "https://neon.com/sitemap-0.xml",
        "blog_sitemap": "https://neon.com/blog-sitemap.xml",
        "pg_sitemap": "https://neon.com/sitemap-postgres.xml",
    }

    def __init__(
        self,
        max_pages: int = 0,
        sources: str = "llms,sitemap",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)  # 0 = unlimited
        self.active_sources = [s.strip() for s in sources.split(",")]
        # Bloom filter: 5K capacity, 0.01% FP rate (~88 KiB memory)
        self.seen: Bloom = Bloom(5000, 0.0001)
        self._stats: dict[str, int] = {
            "discovery_urls": 0,
            "pages_fetched": 0,
            "pages_skipped_dedup": 0,
            "pages_skipped_lang": 0,
            "pages_failed": 0,
            "guides_found": 0,
        }

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Yield requests for each active discovery source."""
        for source_name in self.active_sources:
            url = self.SOURCES.get(source_name)
            if not url:
                self.logger.warning("Unknown source: %s", source_name)
                continue
            self.logger.info("Starting discovery from: %s (%s)", source_name, url)
            if "sitemap" in source_name:
                yield scrapy.Request(
                    url,
                    callback=self.parse_sitemap,
                    cb_kwargs={"source": source_name},
                    errback=self.handle_error,
                )
            else:
                yield scrapy.Request(
                    url,
                    callback=self.parse_llms_txt,
                    cb_kwargs={"source": source_name},
                    errback=self.handle_error,
                )

    def parse_llms_txt(self, response: Response, *, source: str) -> Generator[scrapy.Request | DocPageItem, None, None]:
        """Parse llms.txt and yield requests for each linked page."""
        entries = LLMS_ENTRY_RE.findall(response.text)
        self.logger.info("[%s] Found %d entries in llms.txt", source, len(entries))

        for title, url, description in entries:
            if not self._should_crawl(url):
                continue
            self._stats["discovery_urls"] += 1
            yield scrapy.Request(
                url,
                callback=self.parse_doc_page,
                cb_kwargs={"source": source, "content_type": "page"},
                errback=self.handle_error,
            )

    def parse_sitemap(self, response: Response, *, source: str) -> Generator[scrapy.Request, None, None]:
        """Parse sitemap XML and yield requests for doc pages."""
        urls = SITEMAP_LOC_RE.findall(response.text)
        self.logger.info("[%s] Found %d URLs in sitemap", source, len(urls))

        for url in urls:
            if not self._should_crawl(url):
                continue
            # Classify content type from URL path
            if "/guides/" in url:
                content_type = "guide"
                self._stats["guides_found"] += 1
            elif "/blog/" in url:
                content_type = "blog"
            elif "/postgresql/" in url:
                content_type = "pg_reference"
            elif "/extensions/" in url:
                content_type = "extension"
            elif "/ai/" in url:
                content_type = "ai_guide"
            elif "/changelog/" in url:
                content_type = "changelog"
            else:
                content_type = "page"

            self._stats["discovery_urls"] += 1
            yield scrapy.Request(
                url,
                callback=self.parse_doc_page,
                cb_kwargs={"source": source, "content_type": content_type},
                errback=self.handle_error,
            )

    def parse_doc_page(
        self,
        response: Response,
        *,
        source: str,
        content_type: str,
    ) -> Generator[DocPageItem, None, None]:
        """Extract content from a fetched documentation page."""
        if self.max_pages and self._stats["pages_fetched"] >= self.max_pages:
            return

        self._stats["pages_fetched"] += 1
        text: str = response.text
        content_hash = hashlib.sha256(text.encode()).hexdigest()

        title = self._extract_title(text)
        description = self._extract_description(text)
        headings = self._extract_headings(text)

        item = DocPageItem()
        item["url"] = response.url
        item["title"] = title
        item["description"] = description
        item["headings"] = headings
        item["body_markdown"] = text
        item["content_length"] = len(text)
        item["crawled_at"] = datetime.now(timezone.utc).isoformat()
        item["source"] = source
        item["content_type"] = content_type
        item["content_hash"] = content_hash

        yield item

    def _should_crawl(self, url: str) -> bool:
        """Check URL against bloom filter and language filter."""
        # Language filter
        if LANG_FILTER_RE.search(url):
            self._stats["pages_skipped_lang"] += 1
            return False
        # Max pages guard
        if self.max_pages and self._stats["pages_fetched"] >= self.max_pages:
            return False
        # Bloom dedup
        if url in self.seen:
            self._stats["pages_skipped_dedup"] += 1
            return False
        self.seen.add(url)
        return True

    def handle_error(self, failure: Failure) -> None:
        """Log errors without crashing the crawl."""
        self._stats["pages_failed"] += 1
        self.logger.error("ERROR: %s fetching %s", failure.type.__name__, failure.request.url)

    def closed(self, reason: str) -> None:
        """Log crawl summary stats on spider close."""
        self.logger.info(
            "Crawl complete: discovered=%d fetched=%d dedup_skipped=%d lang_skipped=%d failed=%d guides=%d reason=%s",
            self._stats["discovery_urls"],
            self._stats["pages_fetched"],
            self._stats["pages_skipped_dedup"],
            self._stats["pages_skipped_lang"],
            self._stats["pages_failed"],
            self._stats["guides_found"],
            reason,
        )

    @staticmethod
    def _extract_title(text: str) -> str:
        match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        match = re.search(r"<title>([^<]+)</title>", text)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_description(text: str) -> str:
        match = re.search(r"^>\s*(.+)$", text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', text)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_headings(text: str) -> list[dict[str, Any]]:
        return [
            {"level": len(m.group(1)), "text": m.group(2).strip()}
            for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)
        ]
