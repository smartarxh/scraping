"""
DuckDuckGo search provider implementation
Uses DuckDuckGo HTML interface for search results
"""

import requests
from bs4 import BeautifulSoup
from typing import List
from app.search.search_provider import SearchProvider


class DuckDuckGoProvider(SearchProvider):
    """
    DuckDuckGo search provider.
    """
    
    def __init__(self, max_results: int = 50):
        super().__init__(max_results)
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search(self, query: str) -> List[str]:
        """
        Search DuckDuckGo and return list of URLs.
        """
        urls = []
        
        try:
            params = {
                'q': query,
                'kl': 'en-us'
            }
            
            response = requests.post(
                self.base_url,
                data=params,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Find result links
                results = soup.find_all('a', class_='result__url')
                
                for result in results[:self.max_results]:
                    url = result.get('href')
                    if url and url.startswith('http'):
                        urls.append(url)
                
                # Also check for alternative result structure
                if len(urls) < self.max_results:
                    results = soup.find_all('a', class_='result__a')
                    for result in results[:self.max_results - len(urls)]:
                        url = result.get('href')
                        if url and url.startswith('http'):
                            urls.append(url)
        
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        return urls[:self.max_results]
    
    def get_provider_name(self) -> str:
        return "DuckDuckGo"
