from unittest.mock import MagicMock

import orjson

from agentwarehouses.pipelines.orjson_pipeline import OrjsonWriterPipeline
from agentwarehouses.pipelines.stats_pipeline import StatsValidatorPipeline


class TestOrjsonWriterPipeline:
    def test_write_and_read_item(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        spider = MagicMock()
        spider.logger = MagicMock()

        pipeline = OrjsonWriterPipeline()
        pipeline.open_spider(spider)

        item = {
            "url": "https://example.com/page",
            "title": "Test Page",
            "description": "A test",
            "headings": [{"level": 1, "text": "Test Page"}],
            "body_markdown": "# Test Page\n\nContent here.",
            "content_length": 25,
            "crawled_at": "2026-04-12T00:00:00+00:00",
        }
        pipeline.process_item(item, spider)
        pipeline.close_spider(spider)

        output_file = tmp_path / "output" / "docs.jsonl"
        assert output_file.exists()

        data = orjson.loads(output_file.read_bytes().strip())
        assert data["url"] == "https://example.com/page"
        assert data["title"] == "Test Page"

    def test_process_item_returns_item(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        spider = MagicMock()
        spider.logger = MagicMock()

        pipeline = OrjsonWriterPipeline()
        pipeline.open_spider(spider)

        item = {"url": "https://example.com", "title": "T"}
        result = pipeline.process_item(item, spider)
        assert result is item

        pipeline.close_spider(spider)


class TestStatsValidatorPipeline:
    def _make_item(self, title="Title", description="Desc", body_len=500, heading_count=3):
        return {
            "url": "https://example.com/page",
            "title": title,
            "description": description,
            "headings": [{"level": i + 1, "text": f"H{i + 1}"} for i in range(heading_count)],
            "body_markdown": "x" * body_len,
            "content_length": body_len,
            "crawled_at": "2026-04-12T00:00:00+00:00",
        }

    def test_full_score_passes(self):
        pipeline = StatsValidatorPipeline()
        spider = MagicMock()
        item = self._make_item()
        result = pipeline.process_item(item, spider)
        assert result is item
        assert pipeline.passed == 1
        assert len(pipeline.failed_urls) == 0

    def test_missing_title_still_passes(self):
        """Missing title alone should still pass (score 3/4 >= threshold 3)."""
        pipeline = StatsValidatorPipeline()
        spider = MagicMock()
        item = self._make_item(title="")
        pipeline.process_item(item, spider)
        assert pipeline.passed == 1

    def test_multiple_issues_fails(self):
        """Missing title + short body should fail (score 2/4 < threshold 3)."""
        pipeline = StatsValidatorPipeline()
        spider = MagicMock()
        item = self._make_item(title="", body_len=50)
        pipeline.process_item(item, spider)
        assert pipeline.passed == 0
        assert len(pipeline.failed_urls) == 1
        assert "missing_title" in pipeline.failed_urls[0]["issues"]

    def test_close_spider_logs_summary(self):
        pipeline = StatsValidatorPipeline()
        spider = MagicMock()
        pipeline.process_item(self._make_item(), spider)
        pipeline.process_item(self._make_item(title="", body_len=10, heading_count=0), spider)
        pipeline.close_spider(spider)
        spider.logger.info.assert_called()
