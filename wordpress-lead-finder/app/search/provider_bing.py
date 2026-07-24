"""
Bing search provider implementation
Uses Bing HTML interface for search results
"""

import requests
from bs4 import BeautifulSoup
from typing import List
from app.search.search_provider import SearchProvider


class BingProvider(SearchProvider):
    """
    Bing search provider.
    """
    
    def __init__(self, max_results: int = 50):
        super().__init__(max_results)
        self.base_url = "https://www.bing.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search(self, query: str) -> List[str]:
        """
        Search Bing and return list of URLs.
        """
        urls = []
        
        try:
            params = {
                'q': query,
                'count': self.max_results
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Find result links - Bing uses various structures
                results = soup.find_all('li', class_='b_algo')
                
                for result in results[:self.max_results]:
                    link = result.find('a', href=True)
                    if link:
                        url = link.get('href')
                        if url and url.startswith('http'):
                            urls.append(url)
                
                # Alternative selector
                if len(urls) < self.max_results:
                    results = soup.select('h2 a')
                    for result in results[:self.max_results - len(urls)]:
                        url = result.get('href')
                        if url and url.startswith('http') and not url.startswith('javascript:'):
                            urls.append(url)
        
        except Exception as e:
            print(f"Bing search error: {e}")
        
        return urls[:self.max_results]
    
    def get_provider_name(self) -> str:
        return "Bing"
