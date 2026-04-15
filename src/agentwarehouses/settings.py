BOT_NAME = "Claudebot"

SPIDER_MODULES = ["agentwarehouses.spiders"]
NEWSPIDER_MODULE = "agentwarehouses.spiders"

# Crawl responsibly by identifying ourselves
USER_AGENT = "Claudebot/2.1.109 (+https://code.claude.com/docs)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrent requests tuning
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 0

# Download delay and throttling
DOWNLOAD_DELAY = 0.25

# AutoThrottle - adaptive rate limiting
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 8.0
AUTOTHROTTLE_DEBUG = False

# Retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Download timeout
DOWNLOAD_TIMEOUT = 30

# Disable cookies for crawling public docs
COOKIES_ENABLED = False

# Disable Telnet Console (not needed)
TELNETCONSOLE_ENABLED = False

# Enable pipelines (lower number = higher priority)
ITEM_PIPELINES = {
    "agentwarehouses.pipelines.stats_pipeline.StatsValidatorPipeline": 200,
    "agentwarehouses.pipelines.orjson_pipeline.OrjsonWriterPipeline": 300,
}

# Feed export settings
FEED_EXPORT_ENCODING = "utf-8"

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Logging — colorlog integration
# Scrapy uses its own log setup; we configure compatible defaults here
# and provide agentwarehouses.log.get_logger() for colorized output
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# OTEL telemetry (Claude Code 2.1.109 compatible)
# Set CLAUDE_CODE_ENABLE_TELEMETRY=1 to activate
# See agentwarehouses.log.get_otel_config() for full config reference
