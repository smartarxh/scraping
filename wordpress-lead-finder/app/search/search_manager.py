"""
Search manager that coordinates multiple search providers
"""

import random
from typing import List, Set
from app.search.search_provider import SearchProvider
from app.search.provider_duckduckgo import DuckDuckGoProvider
from app.search.provider_bing import BingProvider
from app.utils.url_utils import normalize_url, extract_root_domain
from app.config import SEARCH_MAX_RESULTS_PER_PROVIDER


class SearchManager:
    """
    Manages multiple search providers and combines results.
    """
    
    def __init__(self, max_results: int = None):
        self.max_results = max_results or SEARCH_MAX_RESULTS_PER_PROVIDER
        self.providers: List[SearchProvider] = [
            DuckDuckGoProvider(self.max_results),
            BingProvider(self.max_results)
        ]
    
    def add_provider(self, provider: SearchProvider):
        """
        Add a custom search provider.
        """
        self.providers.append(provider)
    
    def search(self, query: str) -> List[str]:
        """
        Search using all available providers and combine results.
        
        Args:
            query: Search query string
        
        Returns:
            List of unique, normalized URLs
        """
        all_urls: Set[str] = set()
        
        # Shuffle providers to distribute load
        shuffled_providers = self.providers.copy()
        random.shuffle(shuffled_providers)
        
        for provider in shuffled_providers:
            try:
                urls = provider.search(query)
                for url in urls:
                    normalized = normalize_url(url)
                    if normalized:
                        all_urls.add(normalized)
            except Exception as e:
                print(f"Provider {provider.get_provider_name()} failed: {e}")
                continue
            
            # Stop if we have enough results
            if len(all_urls) >= self.max_results:
                break
        
        return list(all_urls)[:self.max_results]
    
    def search_multiple_queries(self, queries: List[str]) -> List[str]:
        """
        Search using multiple query variations and combine results.
        
        Args:
            queries: List of search query strings
        
        Returns:
            List of unique, normalized URLs
        """
        all_urls: Set[str] = set()
        
        for query in queries:
            urls = self.search(query)
            for url in urls:
                domain = extract_root_domain(url)
                if domain:
                    all_urls.add(url)
            
            # Stop if we have enough results
            if len(all_urls) >= self.max_results:
                break
        
        return list(all_urls)[:self.max_results]
    
    def get_available_providers(self) -> List[str]:
        """
        Return list of available provider names.
        """
        return [p.get_provider_name() for p in self.providers]
