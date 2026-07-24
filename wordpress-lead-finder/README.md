# WordPress Lead Finder

A simple, free, Python-based WordPress Lead Generation Agent.

## Features

- 🔍 **Multi-provider web search** (DuckDuckGo, Bing)
- 🎯 **WordPress detection** using multiple methods
- 📧 **Email extraction** from websites
- 📞 **Phone number extraction**
- 🏢 **Business name extraction**
- 📊 **Export to Excel and CSV**
- 🌐 **Simple web interface**
- ⚡ **Rate-limited crawling** with proper delays
- 🚫 **Excludes social media and directories**

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

Run the application:
```bash
python run.py
```

Open your browser and go to:
```
http://localhost:5000
```

Enter a keyword like "plumber in new york" and click START SEARCH.

### Output

Results are saved in:
```
output/
└── [keyword]/
    ├── [keyword].xlsx
    ├── [keyword].csv
    └── [keyword].log
```

## Configuration

Edit `app/config.py` to customize:

- Crawler timeout and delays
- Maximum pages per website
- WordPress detection thresholds
- Search result limits

### Excluded Domains

Edit `config/excluded_domains.txt` to add domains to exclude (social media, directories, etc.)

## Project Structure

```
wordpress-lead-finder/
│
├── app/
│   ├── main.py                 # Main lead finder logic
│   ├── config.py               # Configuration settings
│   ├── web_interface.py        # Flask web UI
│   │
│   ├── search/
│   │   ├── search_manager.py   # Coordinates search providers
│   │   ├── provider_duckduckgo.py
│   │   └── provider_bing.py
│   │
│   ├── crawler/
│   │   ├── crawler.py          # Web crawler
│   │   └── wordpress_detector.py
│   │
│   ├── extractors/
│   │   ├── email_extractor.py
│   │   ├── phone_extractor.py
│   │   └── business_extractor.py
│   │
│   ├── exporters/
│   │   ├── excel_exporter.py
│   │   └── csv_exporter.py
│   │
│   └── utils/
│       ├── url_utils.py
│       ├── deduplicator.py
│       └── logger.py
│
├── config/
│   └── excluded_domains.txt
│
├── output/                     # Results saved here
│
├── requirements.txt
├── run.py                      # Entry point
└── README.md
```

## Workflow

1. User enters keyword (e.g., "plumber in new york")
2. System searches multiple providers
3. Collects and normalizes URLs
4. Removes duplicates and excluded domains
5. Checks each website for WordPress
6. Extracts contact information from WordPress sites
7. Exports results to Excel and CSV

## Requirements

- Python 3.8+
- requests
- beautifulsoup4
- lxml
- pandas
- openpyxl
- tldextract
- phonenumbers
- flask

All libraries are free and open-source.

## Notes

- The application uses rate limiting to be respectful to websites
- Some websites may not be crawlable due to robots.txt or technical restrictions
- Search providers may have rate limits
- No AI APIs are required - everything runs locally

## License

Free to use for personal and commercial purposes.
