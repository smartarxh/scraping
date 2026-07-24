"""
WordPress detection module
Detects if a website is built with WordPress using multiple methods
"""

from typing import Dict, Tuple
from bs4 import BeautifulSoup


class WordPressDetector:
    """
    Detects WordPress websites using multiple detection methods.
    """
    
    def __init__(self):
        self.wp_indicators = {
            'wp-content': 30,
            'wp-includes': 20,
            'wp-json': 10,
            'wp-admin': 10,
            'wordpress': 15,
        }
        
        self.threshold_confirmed = 70
        self.threshold_likely = 40
    
    def detect(self, html: str, url: str = '') -> Dict:
        """
        Detect if the HTML content is from a WordPress site.
        
        Args:
            html: HTML content of the page
            url: URL of the page (for additional checks)
        
        Returns:
            Dictionary with detection results
        """
        score = 0
        methods_found = []
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Check for wp-content directory
        if 'wp-content' in html:
            score += self.wp_indicators['wp-content']
            methods_found.append('wp-content directory')
        
        # Check for wp-includes directory
        if 'wp-includes' in html:
            score += self.wp_indicators['wp-includes']
            methods_found.append('wp-includes directory')
        
        # Check for wp-json REST API
        if 'wp-json' in html or '/wp-json/' in url:
            score += self.wp_indicators['wp-json']
            methods_found.append('wp-json REST API')
        
        # Check for wp-admin
        if 'wp-admin' in html:
            score += self.wp_indicators['wp-admin']
            methods_found.append('wp-admin reference')
        
        # Check for WordPress meta generator tag
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            content = generator.get('content', '').lower()
            if 'wordpress' in content:
                score += self.wp_indicators['wordpress']
                methods_found.append('WordPress generator meta tag')
        
        # Check for WordPress theme links
        theme_links = soup.find_all('link', href=True)
        for link in theme_links:
            href = link.get('href', '')
            if 'wp-content/themes/' in href:
                score += 15
                methods_found.append('WordPress theme detected')
                break
        
        # Check for WordPress plugin links
        plugin_links = soup.find_all('link', href=True)
        for link in plugin_links:
            href = link.get('href', '')
            if 'wp-content/plugins/' in href:
                score += 15
                methods_found.append('WordPress plugin detected')
                break
        
        # Check for WordPress script sources
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '')
            if 'wp-includes/js/' in src:
                score += 15
                methods_found.append('WordPress core script detected')
                break
        
        # Determine status
        if score >= self.threshold_confirmed:
            status = 'WordPress'
        elif score >= self.threshold_likely:
            status = 'Likely WordPress'
        elif score > 0:
            status = 'Not WordPress'
        else:
            status = 'Unknown'
        
        return {
            'is_wordpress': score >= self.threshold_likely,
            'status': status,
            'confidence': min(score, 100),
            'detection_methods': methods_found,
            'score': score
        }
    
    def is_wordpress(self, html: str, url: str = '') -> bool:
        """
        Quick check if the site is WordPress.
        
        Returns:
            True if WordPress or likely WordPress
        """
        result = self.detect(html, url)
        return result['is_wordpress']
