"""
Email extractor module
Extracts email addresses from HTML content
"""

import re
from typing import List, Set


class EmailExtractor:
    """
    Extracts email addresses from HTML content.
    """
    
    def __init__(self):
        # Email regex pattern
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Common placeholder emails to ignore
        self.placeholder_emails = {
            'example@example.com',
            'email@example.com',
            'test@test.com',
            'demo@demo.com',
            'info@domain.com',
            'contact@website.com',
        }
    
    def extract(self, html: str) -> List[str]:
        """
        Extract email addresses from HTML content.
        
        Args:
            html: HTML content
        
        Returns:
            List of unique email addresses
        """
        if not html:
            return []
        
        # Find all email matches
        emails = re.findall(self.email_pattern, html)
        
        # Also check for mailto: links
        mailto_pattern = r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
        mailto_emails = re.findall(mailto_pattern, html, re.IGNORECASE)
        emails.extend(mailto_emails)
        
        # Normalize and deduplicate
        normalized_emails: Set[str] = set()
        
        for email in emails:
            # Normalize to lowercase
            email_normalized = email.lower().strip()
            
            # Skip placeholder emails
            if email_normalized in self.placeholder_emails:
                continue
            
            # Validate email format (basic validation)
            if self.is_valid_email(email_normalized):
                normalized_emails.add(email_normalized)
        
        return list(normalized_emails)
    
    def is_valid_email(self, email: str) -> bool:
        """
        Basic email validation.
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid
        """
        if not email:
            return False
        
        # Must have @ symbol
        if '@' not in email:
            return False
        
        # Must have domain
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        local, domain = parts
        
        # Local part must not be empty
        if not local:
            return False
        
        # Domain must have at least one dot
        if '.' not in domain:
            return False
        
        # Domain parts must not be empty
        domain_parts = domain.split('.')
        if any(not part for part in domain_parts):
            return False
        
        return True
    
    def extract_from_multiple_pages(self, html_pages: dict) -> List[str]:
        """
        Extract emails from multiple HTML pages.
        
        Args:
            html_pages: Dictionary of URL -> HTML content
        
        Returns:
            List of unique email addresses
        """
        all_emails: Set[str] = set()
        
        for url, html in html_pages.items():
            emails = self.extract(html)
            all_emails.update(emails)
        
        return list(all_emails)
