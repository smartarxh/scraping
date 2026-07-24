"""
Business name extractor module
Extracts business names from HTML content
"""

from typing import Optional
from bs4 import BeautifulSoup


class BusinessNameExtractor:
    """
    Extracts business names from HTML content.
    """
    
    def __init__(self):
        pass
    
    def extract(self, html: str, url: str = '') -> str:
        """
        Extract business name from HTML content.
        
        Args:
            html: HTML content
            url: URL of the page (for fallback)
        
        Returns:
            Business name or 'Unknown'
        """
        if not html:
            return 'Unknown'
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Try multiple methods in order of priority
        
        # 1. Schema.org Organization or LocalBusiness
        name = self._extract_from_schema(soup)
        if name:
            return name
        
        # 2. Open Graph title
        name = self._extract_og_title(soup)
        if name:
            return name
        
        # 3. Meta title
        name = self._extract_meta_title(soup)
        if name:
            return name
        
        # 4. HTML title tag
        name = self._extract_html_title(soup)
        if name:
            return name
        
        # 5. H1 tag
        name = self._extract_h1(soup)
        if name:
            return name
        
        # 6. Domain name as fallback
        name = self._extract_from_domain(url)
        if name:
            return name
        
        return 'Unknown'
    
    def _extract_from_schema(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract name from Schema.org structured data.
        """
        # Look for JSON-LD schema
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                import json
                content = script.string
                if content:
                    schema = json.loads(content.strip())
                    
                    # Handle array of schemas
                    if isinstance(schema, list):
                        for item in schema:
                            name = self._parse_schema_item(item)
                            if name:
                                return name
                    else:
                        name = self._parse_schema_item(schema)
                        if name:
                            return name
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Look for microdata
        items = soup.find_all(attrs={'itemtype': True})
        for item in items:
            itemtype = item.get('itemtype', '').lower()
            if 'organization' in itemtype or 'localbusiness' in itemtype:
                name_elem = item.find(attrs={'itemprop': 'name'})
                if name_elem and name_elem.string:
                    return name_elem.string.strip()
        
        return None
    
    def _parse_schema_item(self, schema: dict) -> Optional[str]:
        """
        Parse a schema item and extract name.
        """
        schema_type = schema.get('@type', '')
        
        if isinstance(schema_type, str):
            schema_type = schema_type.lower()
        elif isinstance(schema_type, list):
            schema_type = [t.lower() for t in schema_type]
        else:
            schema_type = ''
        
        if 'organization' in str(schema_type) or 'localbusiness' in str(schema_type):
            name = schema.get('name')
            if name and isinstance(name, str):
                return name.strip()
        
        return None
    
    def _extract_og_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract from Open Graph title.
        """
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title.get('content').strip()
        return None
    
    def _extract_meta_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract from meta title tag.
        """
        meta_title = soup.find('meta', attrs={'name': 'title'})
        if meta_title and meta_title.get('content'):
            return meta_title.get('content').strip()
        return None
    
    def _extract_html_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract from HTML title tag.
        """
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            # Clean up common patterns
            if ' - ' in title:
                title = title.split(' - ')[0]
            if ' | ' in title:
                title = title.split(' | ')[0]
            return title.strip()
        return None
    
    def _extract_h1(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract from H1 tag.
        """
        h1 = soup.find('h1')
        if h1 and h1.string:
            return h1.string.strip()
        return None
    
    def _extract_from_domain(self, url: str) -> Optional[str]:
        """
        Extract business name from domain as fallback.
        """
        if not url:
            return None
        
        from app.utils.url_utils import extract_root_domain
        domain = extract_root_domain(url)
        
        if domain:
            # Remove TLD
            name = domain.split('.')[0]
            # Capitalize
            return name.capitalize()
        
        return None
