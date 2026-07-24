"""
Configuration settings for WordPress Lead Finder
"""

# Crawler settings
CRAWLER_TIMEOUT = 15  # seconds
CRAWLER_MAX_PAGES = 5
CRAWLER_RETRIES = 2
CRAWLER_MIN_DELAY = 2  # seconds
CRAWLER_MAX_DELAY = 5  # seconds

# WordPress detection thresholds
WP_THRESHOLD_CONFIRMED = 70  # percentage
WP_THRESHOLD_LIKELY = 40  # percentage

# Search settings
SEARCH_MAX_RESULTS_PER_PROVIDER = 50
SEARCH_PROVIDERS = ['google', 'bing', 'duckduckgo']

# Output settings
OUTPUT_DIR = 'output'

# Logging settings
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
