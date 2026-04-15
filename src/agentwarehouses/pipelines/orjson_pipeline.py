from __future__ import annotations

import os
from io import BufferedWriter
from pathlib import Path
from typing import Any

import orjson
import scrapy


class OrjsonWriterPipeline:
    """Write each crawled item as a JSON line using orjson for speed.

    Output goes to ``output/docs.jsonl`` relative to the working directory.
    Each line is a compact, UTF-8 JSON object.
    """

    file: BufferedWriter

    def open_spider(self, spider: scrapy.Spider) -> None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        self.file = open(output_dir / "docs.jsonl", "wb")
        spider.logger.info("OrjsonWriterPipeline: writing to %s", output_dir / "docs.jsonl")

    def close_spider(self, spider: scrapy.Spider) -> None:
        self.file.close()
        size: int = os.path.getsize(Path("output") / "docs.jsonl")
        spider.logger.info("OrjsonWriterPipeline: wrote %d bytes", size)

    def process_item(self, item: Any, spider: scrapy.Spider) -> Any:
        line: bytes = orjson.dumps(dict(item), option=orjson.OPT_APPEND_NEWLINE)
        self.file.write(line)
        return item
