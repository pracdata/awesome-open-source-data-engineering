from __future__ import annotations

import logging
from typing import Any

import scrapy

logger: logging.Logger = logging.getLogger(__name__)


class StatsValidatorPipeline:
    """Grade each crawled page for completeness and flag quality issues.

    Inspired by the evaluator-optimizer pattern: grade outcomes, not paths.
    Each item is scored on four criteria. Items with score < threshold
    are logged as warnings for investigation.
    """

    PASS_THRESHOLD: int = 3  # out of 4

    def __init__(self) -> None:
        self.total: int = 0
        self.passed: int = 0
        self.failed_urls: list[dict[str, Any]] = []

    def process_item(self, item: Any, spider: scrapy.Spider) -> Any:
        self.total += 1
        score: int = 0
        issues: list[str] = []

        # Criterion 1: title extracted
        if item.get("title"):
            score += 1
        else:
            issues.append("missing_title")

        # Criterion 2: description extracted
        if item.get("description"):
            score += 1
        else:
            issues.append("missing_description")

        # Criterion 3: body is substantive (>100 chars)
        body_len: int = item.get("content_length", 0)
        if body_len > 100:
            score += 1
        else:
            issues.append(f"short_body({body_len})")

        # Criterion 4: headings structure present
        headings: list[Any] = item.get("headings", [])
        if len(headings) >= 2:
            score += 1
        else:
            issues.append(f"few_headings({len(headings)})")

        if score >= self.PASS_THRESHOLD:
            self.passed += 1
        else:
            self.failed_urls.append({"url": item["url"], "score": score, "issues": issues})
            logger.warning("QUALITY: %s score=%d/4 issues=%s", item["url"], score, ",".join(issues))

        return item

    def close_spider(self, spider: scrapy.Spider) -> None:
        spider.logger.info(
            "Quality gate: %d/%d passed (threshold=%d/4), %d flagged",
            self.passed,
            self.total,
            self.PASS_THRESHOLD,
            len(self.failed_urls),
        )
        for f in self.failed_urls:
            spider.logger.info("  FLAGGED: %s score=%d issues=%s", f["url"], f["score"], ",".join(f["issues"]))
