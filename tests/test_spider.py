"""Tests for the llmstxt spider — unit tests and Scrapy response integration tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from scrapy.http import TextResponse

from agentwarehouses.spiders.llmstxt_spider import LlmstxtSpider

SAMPLE_LLMS_TXT = """\
# Claude Code Docs

- [Overview](https://code.claude.com/docs/en/overview.md): Claude Code overview
- [Quickstart](https://code.claude.com/docs/en/quickstart.md): Get started
- [Settings](https://code.claude.com/docs/en/settings.md): Configure Claude Code
"""

SAMPLE_DOC_PAGE = """\
# Claude Code overview

> An agentic coding tool for your terminal

## Getting started

Install Claude Code and start coding.

## Features

- Code editing
- File search
"""


@pytest.mark.unit
class TestLlmstxtSpiderInit:
    def test_spider_name(self) -> None:
        spider = LlmstxtSpider()
        assert spider.name == "llmstxt"

    def test_default_index_url(self) -> None:
        spider = LlmstxtSpider()
        assert spider.index_url == "https://code.claude.com/docs/llms.txt"
        assert spider.start_urls == ["https://code.claude.com/docs/llms.txt"]

    def test_custom_index_url(self) -> None:
        spider = LlmstxtSpider(index_url="https://example.com/llms.txt")
        assert spider.index_url == "https://example.com/llms.txt"

    def test_bloom_filter_initialized(self) -> None:
        spider = LlmstxtSpider()
        assert spider.seen is not None
        spider.seen.add("https://example.com/test")
        assert "https://example.com/test" in spider.seen
        assert "https://example.com/other" not in spider.seen

    def test_allowed_domains(self) -> None:
        spider = LlmstxtSpider()
        assert spider.allowed_domains == ["code.claude.com"]

    def test_stats_initialized(self) -> None:
        spider = LlmstxtSpider()
        assert spider._stats == {"index_urls": 0, "pages_fetched": 0, "pages_failed": 0}

    def test_custom_settings_type(self) -> None:
        assert isinstance(LlmstxtSpider.custom_settings, dict)
        assert LlmstxtSpider.custom_settings["CONCURRENT_REQUESTS"] == 16


@pytest.mark.unit
class TestExtractMethods:
    def test_extract_title(self) -> None:
        assert LlmstxtSpider._extract_title("# My Title\n\nContent") == "My Title"

    def test_extract_title_missing(self) -> None:
        assert LlmstxtSpider._extract_title("No heading here") == ""

    def test_extract_title_with_whitespace(self) -> None:
        assert LlmstxtSpider._extract_title("#   Padded Title  \n") == "Padded Title"

    def test_extract_description(self) -> None:
        assert LlmstxtSpider._extract_description("# T\n\n> Description here") == "Description here"

    def test_extract_description_missing(self) -> None:
        assert LlmstxtSpider._extract_description("# T\n\nNo blockquote") == ""

    def test_extract_headings(self) -> None:
        text = "# Title\n## Section One\n### Subsection\n## Section Two"
        headings = LlmstxtSpider._extract_headings(text)
        assert len(headings) == 4
        assert headings[0] == {"level": 1, "text": "Title"}
        assert headings[1] == {"level": 2, "text": "Section One"}
        assert headings[2] == {"level": 3, "text": "Subsection"}
        assert headings[3] == {"level": 2, "text": "Section Two"}

    def test_extract_headings_empty(self) -> None:
        assert LlmstxtSpider._extract_headings("Plain text") == []

    def test_extract_headings_h6(self) -> None:
        headings = LlmstxtSpider._extract_headings("###### Deep heading")
        assert headings == [{"level": 6, "text": "Deep heading"}]


@pytest.mark.integration
class TestParseIndex:
    def _fake_response(self, body: str, url: str = "https://code.claude.com/docs/llms.txt") -> TextResponse:
        return TextResponse(url=url, body=body.encode("utf-8"))

    def test_parse_extracts_urls(self) -> None:
        spider = LlmstxtSpider()
        response = self._fake_response(SAMPLE_LLMS_TXT)
        requests = list(spider.parse(response))
        assert len(requests) == 3
        assert requests[0].url == "https://code.claude.com/docs/en/overview.md"

    def test_parse_updates_stats(self) -> None:
        spider = LlmstxtSpider()
        response = self._fake_response(SAMPLE_LLMS_TXT)
        list(spider.parse(response))
        assert spider._stats["index_urls"] == 3

    def test_parse_deduplicates(self) -> None:
        spider = LlmstxtSpider()
        body = SAMPLE_LLMS_TXT + "\n- [Dup](https://code.claude.com/docs/en/overview.md): duplicate"
        response = self._fake_response(body)
        requests = list(spider.parse(response))
        urls = [r.url for r in requests]
        assert urls.count("https://code.claude.com/docs/en/overview.md") == 1

    def test_parse_empty_index(self) -> None:
        spider = LlmstxtSpider()
        response = self._fake_response("# Empty index\nNo URLs here")
        requests = list(spider.parse(response))
        assert len(requests) == 0
        assert spider._stats["index_urls"] == 0

    def test_parse_sets_errback(self) -> None:
        spider = LlmstxtSpider()
        response = self._fake_response(SAMPLE_LLMS_TXT)
        requests = list(spider.parse(response))
        assert requests[0].errback is not None


@pytest.mark.integration
class TestParseDocPage:
    def _fake_response(self, body: str, url: str = "https://code.claude.com/docs/en/overview.md") -> TextResponse:
        return TextResponse(url=url, body=body.encode("utf-8"))

    def test_parse_doc_page_yields_item(self) -> None:
        spider = LlmstxtSpider()
        response = self._fake_response(SAMPLE_DOC_PAGE)
        items = list(spider.parse_doc_page(response))
        assert len(items) == 1

    def test_parse_doc_page_extracts_fields(self) -> None:
        spider = LlmstxtSpider()
        response = self._fake_response(SAMPLE_DOC_PAGE)
        item = list(spider.parse_doc_page(response))[0]
        assert item["url"] == "https://code.claude.com/docs/en/overview.md"
        assert item["title"] == "Claude Code overview"
        assert item["description"] == "An agentic coding tool for your terminal"
        assert len(item["headings"]) == 3
        assert item["content_length"] > 100
        assert item["crawled_at"].endswith("+00:00")

    def test_parse_doc_page_increments_stats(self) -> None:
        spider = LlmstxtSpider()
        response = self._fake_response(SAMPLE_DOC_PAGE)
        list(spider.parse_doc_page(response))
        assert spider._stats["pages_fetched"] == 1

    def test_parse_doc_page_empty_body(self) -> None:
        spider = LlmstxtSpider()
        response = self._fake_response("")
        item = list(spider.parse_doc_page(response))[0]
        assert item["title"] == ""
        assert item["description"] == ""
        assert item["content_length"] == 0


@pytest.mark.integration
class TestHandleError:
    def test_handle_error_increments_failed_stats(self) -> None:
        spider = LlmstxtSpider()
        failure = MagicMock()
        failure.request.url = "https://example.com/broken"
        failure.check.return_value = False
        failure.type.__name__ = "SomeError"
        spider.handle_error(failure)
        assert spider._stats["pages_failed"] == 1

    def test_handle_error_http_error(self) -> None:
        spider = LlmstxtSpider()
        failure = MagicMock()
        failure.request.url = "https://example.com/404"
        failure.check.side_effect = lambda cls: cls.__name__ == "HttpError"
        failure.value.response.status = 404

        # Mock HttpError check
        from scrapy.spidermiddlewares.httperror import HttpError

        failure.check.side_effect = lambda cls: cls is HttpError
        spider.handle_error(failure)
        assert spider._stats["pages_failed"] == 1


@pytest.mark.unit
class TestClosedMethod:
    def test_closed_logs_stats(self) -> None:
        spider = LlmstxtSpider()
        spider._stats = {"index_urls": 10, "pages_fetched": 8, "pages_failed": 2}
        # closed() just logs, should not raise
        spider.closed("finished")
