"""
DuckDuckGo search provider implementation
Uses ddgs library for reliable search results
"""

from typing import List
from app.search.search_provider import SearchProvider


class DuckDuckGoProvider(SearchProvider):
    """
    DuckDuckGo search provider using ddgs library.
    """
    
    def __init__(self, max_results: int = 50):
        super().__init__(max_results)
    
    def search(self, query: str) -> List[str]:
        """
        Search DuckDuckGo and return list of URLs.
        """
        urls = []
        
        try:
            from ddgs import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
                
                for result in results:
                    href = result.get('href')
                    if href and href.startswith('http'):
                        urls.append(href)
        
        except ImportError:
            print("ddgs library not installed. Run: pip install ddgs")
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        return urls[:self.max_results]
    
    def get_provider_name(self) -> str:
        return "DuckDuckGo"
