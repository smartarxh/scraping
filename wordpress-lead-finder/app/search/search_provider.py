"""
Base class for search providers
"""

from abc import ABC, abstractmethod
from typing import List


class SearchProvider(ABC):
    """
    Abstract base class for search providers.
    """
    
    def __init__(self, max_results: int = 50):
        self.max_results = max_results
    
    @abstractmethod
    def search(self, query: str) -> List[str]:
        """
        Perform a search and return list of URLs.
        
        Args:
            query: Search query string
        
        Returns:
            List of URLs from search results
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the name of the search provider.
        """
        pass
