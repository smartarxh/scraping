"""
URL utility functions for normalization and domain extraction
"""

import re
from urllib.parse import urlparse, urlunparse
import tldextract


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing fragments, normalizing protocol and www.
    Returns the normalized URL.
    """
    if not url:
        return ''
    
    # Ensure URL has a scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    
    # Remove fragment
    fragment = ''
    
    # Normalize scheme to https
    scheme = 'https'
    
    # Remove www from netloc
    netloc = parsed.netloc.lower()
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    
    # Remove common tracking parameters
    query_params = []
    for param in parsed.query.split('&'):
        if param and not param.startswith(('utm_', 'fbclid', 'gclid', 'ref=')):
            query_params.append(param)
    query = '&'.join(query_params)
    
    # Remove trailing slash from path
    path = parsed.path.rstrip('/')
    if not path:
        path = '/'
    
    normalized = urlunparse((scheme, netloc, path, parsed.params, query, fragment))
    return normalized


def extract_root_domain(url: str) -> str:
    """
    Extract the root domain from a URL.
    Example: https://www.example.com/contact -> example.com
    """
    if not url:
        return ''
    
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    return domain.lower()


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def remove_duplicate_urls(urls: list) -> list:
    """
    Remove duplicate URLs based on root domain.
    Returns list of unique URLs with their domains.
    """
    seen_domains = set()
    unique_urls = []
    
    for url in urls:
        domain = extract_root_domain(url)
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            unique_urls.append(url)
    
    return unique_urls


def get_domain_from_url(url: str) -> str:
    """
    Get the full domain (including subdomain) from a URL.
    """
    if not url:
        return ''
    
    parsed = urlparse(url)
    return parsed.netloc.lower()
