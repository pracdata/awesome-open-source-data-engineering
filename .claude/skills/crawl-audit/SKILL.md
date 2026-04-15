---
name: crawl-audit
description: Audit crawl output for completeness, quality, and deduplication issues
disable-model-invocation: false
---
# Crawl Audit

## When to use
After running `scrapy crawl llmstxt` to validate output quality before downstream consumption.

## Instructions

1. **Check output exists**: Verify `output/docs.jsonl` was created and is non-empty
2. **Count pages**: Compare number of JSONL lines against expected page count from llms.txt
3. **Validate structure**: Each line must have: `url`, `title`, `description`, `body_markdown`, `crawled_at`
4. **Check for blanks**: Flag pages where `title` or `body_markdown` is empty
5. **Check dedup**: Verify no duplicate URLs appear in output
6. **Size audit**: Flag pages where `body_markdown` is under 100 chars (likely fetch failures)
7. **Report**: Print summary table with pass/fail per check

## Verification script

```bash
# Quick audit one-liner
python -c "
import orjson, sys
from pathlib import Path
data = Path('output/docs.jsonl').read_bytes().strip().split(b'\n')
pages = [orjson.loads(line) for line in data]
urls = [p['url'] for p in pages]
print(f'Pages: {len(pages)}')
print(f'Unique URLs: {len(set(urls))}')
print(f'Duplicates: {len(urls) - len(set(urls))}')
empty_title = sum(1 for p in pages if not p.get('title'))
short_body = sum(1 for p in pages if len(p.get('body_markdown','')) < 100)
print(f'Empty titles: {empty_title}')
print(f'Short bodies (<100 chars): {short_body}')
print('PASS' if empty_title == 0 and short_body == 0 and len(urls) == len(set(urls)) else 'FAIL')
"
```

## Example output
```
Pages: 98
Unique URLs: 98
Duplicates: 0
Empty titles: 0
Short bodies (<100 chars): 0
PASS
```
