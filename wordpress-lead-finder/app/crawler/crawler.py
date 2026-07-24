"""
Web crawler for fetching and parsing website content
"""

import time
import random
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from app.config import (
    CRAWLER_TIMEOUT,
    CRAWLER_MAX_PAGES,
    CRAWLER_RETRIES,
    CRAWLER_MIN_DELAY,
    CRAWLER_MAX_DELAY
)
from app.utils.url_utils import normalize_url, extract_root_domain, is_valid_url


class WebCrawler:
    """
    Web crawler for fetching and parsing website content.
    """
    
    def __init__(self):
        self.timeout = CRAWLER_TIMEOUT
        self.max_pages = CRAWLER_MAX_PAGES
        self.retries = CRAWLER_RETRIES
        self.min_delay = CRAWLER_MIN_DELAY
        self.max_delay = CRAWLER_MAX_DELAY
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a single page and return HTML content.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content or None if failed
        """
        for attempt in range(self.retries + 1):
            try:
                # Add random delay
                delay = random.uniform(self.min_delay, self.max_delay)
                time.sleep(delay)
                
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    time.sleep(10)
                    continue
                elif response.status_code >= 400:
                    # Client or server error
                    return None
                
            except requests.exceptions.Timeout:
                print(f"Timeout fetching {url}")
            except requests.exceptions.SSLError:
                print(f"SSL error fetching {url}")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")
            
            if attempt < self.retries:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def find_contact_pages(self, html: str, base_url: str) -> List[str]:
        """
        Find contact and about page links from HTML.
        
        Args:
            html: HTML content
            base_url: Base URL of the website
        
        Returns:
            List of contact/about page URLs
        """
        contact_keywords = [
            'contact', 'contact-us', 'contactus',
            'about', 'about-us', 'aboutus',
            'get-in-touch', 'reach-us', 'getintouch'
        ]
        
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find_all('a', href=True)
        
        found_urls = []
        root_domain = extract_root_domain(base_url)
        
        for link in links:
            href = link.get('href', '')
            
            # Skip non-HTTP links
            if not href.startswith(('http', '/')):
                continue
            
            # Convert relative to absolute URL
            if href.startswith('/'):
                parsed_base = requests.utils.urlparse(base_url)
                href = f"{parsed_base.scheme}://{parsed_base.netloc}{href}"
            
            # Check if same domain
            link_domain = extract_root_domain(href)
            if link_domain != root_domain:
                continue
            
            # Check for contact keywords
            href_lower = href.lower()
            for keyword in contact_keywords:
                if keyword in href_lower:
                    normalized = normalize_url(href)
                    if normalized and normalized not in found_urls:
                        found_urls.append(normalized)
                    break
        
        return found_urls[:self.max_pages]
    
    def crawl_website(self, url: str) -> Dict:
        """
        Crawl a website and collect pages for analysis.
        
        Args:
            url: Homepage URL
        
        Returns:
            Dictionary with crawled data
        """
        result = {
            'homepage_html': None,
            'contact_pages': [],
            'all_html': {},
            'status': 'success'
        }
        
        # Fetch homepage
        homepage_html = self.fetch_page(url)
        if not homepage_html:
            result['status'] = 'failed'
            return result
        
        result['homepage_html'] = homepage_html
        result['all_html'][url] = homepage_html
        
        # Find contact pages
        contact_pages = self.find_contact_pages(homepage_html, url)
        result['contact_pages'] = contact_pages
        
        # Fetch contact pages
        for contact_url in contact_pages:
            html = self.fetch_page(contact_url)
            if html:
                result['all_html'][contact_url] = html
        
        return result
    
    def close(self):
        """
        Close the session.
        """
        self.session.close()
