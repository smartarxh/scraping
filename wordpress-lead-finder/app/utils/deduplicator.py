"""
Deduplicator utility for removing duplicate leads
"""

from app.utils.url_utils import extract_root_domain


class Deduplicator:
    """
    Handles deduplication of leads based on various criteria.
    """
    
    def __init__(self):
        self.seen_domains = set()
        self.seen_emails = set()
        self.seen_urls = set()
    
    def is_duplicate_domain(self, url: str) -> bool:
        """
        Check if a domain has already been processed.
        """
        domain = extract_root_domain(url)
        if domain in self.seen_domains:
            return True
        self.seen_domains.add(domain)
        return False
    
    def is_duplicate_email(self, email: str) -> bool:
        """
        Check if an email has already been seen.
        """
        email_normalized = email.lower().strip()
        if email_normalized in self.seen_emails:
            return True
        self.seen_emails.add(email_normalized)
        return False
    
    def is_duplicate_url(self, url: str) -> bool:
        """
        Check if a URL has already been processed.
        """
        if url in self.seen_urls:
            return True
        self.seen_urls.add(url)
        return False
    
    def reset(self):
        """
        Reset all tracking sets.
        """
        self.seen_domains.clear()
        self.seen_emails.clear()
        self.seen_urls.clear()
    
    def deduplicate_leads(self, leads: list) -> list:
        """
        Remove duplicate leads from a list based on domain.
        
        Args:
            leads: List of lead dictionaries
        
        Returns:
            List of unique leads
        """
        seen_domains = set()
        unique_leads = []
        
        for lead in leads:
            domain = extract_root_domain(lead.get('website_url', ''))
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                unique_leads.append(lead)
        
        return unique_leads
