"""
Main lead finder module that orchestrates the entire workflow
"""

import os
import random
from datetime import datetime
from typing import List, Dict, Tuple

from app.config import OUTPUT_DIR
from app.utils.logger import sanitize_filename
from app.utils.url_utils import normalize_url, extract_root_domain
from app.utils.deduplicator import Deduplicator
from app.search.search_manager import SearchManager
from app.crawler.crawler import WebCrawler
from app.crawler.wordpress_detector import WordPressDetector
from app.extractors.email_extractor import EmailExtractor
from app.extractors.phone_extractor import PhoneExtractor
from app.extractors.business_extractor import BusinessNameExtractor
from app.exporters.excel_exporter import ExcelExporter
from app.exporters.csv_exporter import CSVExporter


class LeadFinder:
    """
    Main class that orchestrates the lead finding workflow.
    """
    
    def __init__(self, max_websites: int = 100):
        self.max_websites = max_websites
        self.search_manager = SearchManager(max_results=max_websites)
        self.crawler = WebCrawler()
        self.wp_detector = WordPressDetector()
        self.email_extractor = EmailExtractor()
        self.phone_extractor = PhoneExtractor()
        self.business_extractor = BusinessNameExtractor()
        self.excel_exporter = ExcelExporter()
        self.csv_exporter = CSVExporter()
        self.deduplicator = Deduplicator()
        
        # Statistics
        self.stats = {
            'websites_found': 0,
            'unique_domains': 0,
            'wordpress_checked': 0,
            'wordpress_found': 0,
            'contacts_extracted': 0,
            'emails_found': 0,
            'phones_found': 0,
            'leads_saved': 0
        }
        
        # Excluded domains
        self.excluded_domains = set()
        self._load_excluded_domains()
    
    def _load_excluded_domains(self):
        """Load excluded domains from config file."""
        config_path = os.path.join('config', 'excluded_domains.txt')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    domain = line.strip().lower()
                    if domain:
                        self.excluded_domains.add(domain)
    
    def generate_search_queries(self, keyword: str) -> List[str]:
        """
        Generate multiple search query variations.
        """
        queries = [keyword]
        
        # Extract main terms
        words = keyword.lower().split()
        
        # Generate variations
        variations = []
        
        # Add service-related terms
        if 'plumber' in keyword or 'plumbing' in keyword:
            variations.extend([
                f"plumbing companies in {' '.join(words[-2:])}" if len(words) > 2 else keyword,
                f"plumbing services {' '.join(words[-2:])}" if len(words) > 2 else keyword,
                f"local plumbers {' '.join(words[-2:])}" if len(words) > 2 else keyword,
            ])
        
        # Generic variations for any keyword
        if len(words) >= 3:
            location = ' '.join(words[-2:])
            service = words[0]
            variations.append(f"{service} companies in {location}")
            variations.append(f"{service} services {location}")
            variations.append(f"local {service} {location}")
        
        # Add unique variations
        for var in variations:
            if var not in queries:
                queries.append(var)
        
        return queries[:5]  # Limit to 5 queries
    
    def is_excluded_domain(self, url: str) -> bool:
        """
        Check if URL belongs to an excluded domain.
        """
        domain = extract_root_domain(url).lower()
        return domain in self.excluded_domains
    
    def find_leads(self, keyword: str, progress_callback=None) -> Tuple[List[Dict], str]:
        """
        Main method to find leads for a keyword.
        
        Args:
            keyword: Search keyword
            progress_callback: Optional callback for progress updates
        
        Returns:
            Tuple of (leads list, output directory path)
        """
        leads = []
        safe_keyword = sanitize_filename(keyword)
        output_dir = os.path.join(OUTPUT_DIR, safe_keyword)
        os.makedirs(output_dir, exist_ok=True)
        
        # Reset stats
        self.stats = {k: 0 for k in self.stats}
        
        if progress_callback:
            progress_callback('Searching...', 0)
        
        # Generate search queries
        queries = self.generate_search_queries(keyword)
        
        # Search for websites
        all_urls = self.search_manager.search_multiple_queries(queries)
        self.stats['websites_found'] = len(all_urls)
        
        if progress_callback:
            progress_callback(f'Search completed - {len(all_urls)} websites found', 10)
        
        # Filter excluded domains and deduplicate
        filtered_urls = []
        seen_domains = set()
        
        for url in all_urls:
            domain = extract_root_domain(url)
            
            # Skip excluded domains
            if self.is_excluded_domain(url):
                continue
            
            # Skip already seen domains
            if domain in seen_domains:
                continue
            
            seen_domains.add(domain)
            filtered_urls.append(url)
        
        self.stats['unique_domains'] = len(filtered_urls)
        
        if progress_callback:
            progress_callback(f'{len(filtered_urls)} unique domains after filtering', 15)
        
        # Process each website
        wordpress_urls = []
        
        for i, url in enumerate(filtered_urls):
            if progress_callback:
                progress = 15 + int((i / len(filtered_urls)) * 30)
                progress_callback(f'Checking WordPress: {i+1}/{len(filtered_urls)}', progress)
            
            self.stats['wordpress_checked'] += 1
            
            # Crawl website
            crawl_data = self.crawler.crawl_website(url)
            
            if crawl_data['status'] == 'failed':
                continue
            
            # Detect WordPress
            wp_result = self.wp_detector.detect(
                crawl_data['homepage_html'],
                url
            )
            
            if not wp_result['is_wordpress']:
                continue
            
            self.stats['wordpress_found'] += 1
            wordpress_urls.append((url, crawl_data, wp_result))
        
        if progress_callback:
            progress_callback(f'{len(wordpress_urls)} WordPress websites found', 45)
        
        # Extract contact information from WordPress sites
        for i, (url, crawl_data, wp_result) in enumerate(wordpress_urls):
            if progress_callback:
                progress = 45 + int((i / len(wordpress_urls)) * 35)
                progress_callback(f'Extracting contacts: {i+1}/{len(wordpress_urls)}', progress)
            
            self.stats['contacts_extracted'] += 1
            
            # Combine all HTML from crawled pages
            all_html = '\n'.join(crawl_data['all_html'].values())
            
            # Extract business name
            business_name = self.business_extractor.extract(
                crawl_data['homepage_html'],
                url
            )
            
            # Extract emails
            emails = self.email_extractor.extract_from_multiple_pages(crawl_data['all_html'])
            self.stats['emails_found'] += len(emails)
            
            # Extract phones
            phones = self.phone_extractor.extract_from_multiple_pages(crawl_data['all_html'])
            self.stats['phones_found'] += len(phones)
            
            # Get first email and phone (or N/A)
            email = emails[0] if emails else 'N/A'
            phone = phones[0] if phones else 'N/A'
            
            # Get contact page URL
            contact_page = crawl_data['contact_pages'][0] if crawl_data['contact_pages'] else url
            
            # Create lead
            lead = {
                'Business Name': business_name,
                'Website URL': url,
                'Domain': extract_root_domain(url),
                'CMS': 'WordPress',
                'WordPress Confidence': wp_result['confidence'],
                'Email': email,
                'Phone': phone,
                'Contact Page': contact_page,
                'Search Keyword': keyword,
                'Source': 'Web Search',
                'Date Found': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            leads.append(lead)
        
        self.stats['leads_saved'] = len(leads)
        
        if progress_callback:
            progress_callback('Exporting results...', 80)
        
        # Remove duplicate leads
        leads = self.deduplicator.deduplicate_leads(leads)
        
        # Export results
        base_filename = safe_keyword
        excel_path = os.path.join(output_dir, f"{base_filename}.xlsx")
        csv_path = os.path.join(output_dir, f"{base_filename}.csv")
        
        self.excel_exporter.export(leads, excel_path)
        self.csv_exporter.export(leads, csv_path)
        
        if progress_callback:
            progress_callback('Completed!', 100)
        
        return leads, output_dir
    
    def get_stats(self) -> Dict:
        """Return current statistics."""
        return self.stats
    
    def close(self):
        """Clean up resources."""
        self.crawler.close()
