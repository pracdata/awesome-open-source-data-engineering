When working on this project:

- The crawler uses Scrapy with BOT_NAME "Claudebot" and USER_AGENT identifying as Claudebot/2.1.109
- Always obey robots.txt (ROBOTSTXT_OBEY = True)
- Use rbloom Bloom filters for URL deduplication, not sets (memory efficient)
- Use orjson for all JSON serialization (faster than stdlib json)
- Output goes to output/docs.jsonl as newline-delimited JSON
- The llms.txt spider targets https://code.claude.com/docs/llms.txt as the entry point
- Concurrency is tuned via AUTOTHROTTLE for adaptive rate limiting
- Run the crawler with: scrapy crawl llmstxt
