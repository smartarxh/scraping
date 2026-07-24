"""
Phone number extractor module
Extracts phone numbers from HTML content
"""

import re
from typing import List, Set, Optional
import phonenumbers
from phonenumbers import NumberParseException


class PhoneExtractor:
    """
    Extracts phone numbers from HTML content.
    """
    
    def __init__(self):
        # Phone number patterns
        self.phone_patterns = [
            # International format: +1 234 567 8900
            r'\+\d[\d\s\-\(\)]{7,}\d',
            # US format: (234) 567-8900
            r'\(\d{3}\)\s*\d{3}[\-\s]?\d{4}',
            # US format: 234-567-8900
            r'\d{3}[\-\.\s]\d{3}[\-\.\s]\d{4}',
            # Simple format: 2345678900
            r'\b\d{10}\b',
        ]
    
    def extract(self, html: str, default_country: str = 'US') -> List[str]:
        """
        Extract phone numbers from HTML content.
        
        Args:
            html: HTML content
            default_country: Default country code for parsing
        
        Returns:
            List of unique phone numbers (original format)
        """
        if not html:
            return []
        
        found_phones: Set[str] = set()
        
        # Find tel: links first
        tel_pattern = r'tel:([^\s"\'>]+)'
        tel_matches = re.findall(tel_pattern, html, re.IGNORECASE)
        for match in tel_matches:
            cleaned = self.clean_phone_number(match)
            if cleaned:
                found_phones.add(cleaned)
        
        # Find phone numbers using patterns
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                cleaned = self.clean_phone_number(match)
                if cleaned:
                    found_phones.add(cleaned)
        
        return list(found_phones)
    
    def clean_phone_number(self, phone: str) -> Optional[str]:
        """
        Clean and validate a phone number.
        
        Args:
            phone: Raw phone number string
        
        Returns:
            Cleaned phone number or None if invalid
        """
        if not phone:
            return None
        
        # Remove common prefixes
        phone = phone.replace('tel:', '').replace('TEL:', '')
        phone = phone.strip()
        
        # Remove excessive whitespace
        phone = ' '.join(phone.split())
        
        # Basic validation - must have digits
        if not any(c.isdigit() for c in phone):
            return None
        
        # Must have reasonable length (at least 7 digits)
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 7 or len(digits_only) > 15:
            return None
        
        return phone
    
    def normalize_phone(self, phone: str, default_country: str = 'US') -> Optional[str]:
        """
        Normalize phone number to international format.
        
        Args:
            phone: Phone number string
            default_country: Default country code
        
        Returns:
            Normalized phone number or None if invalid
        """
        try:
            parsed = phonenumbers.parse(phone, default_country)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(
                    parsed,
                    phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
        except NumberParseException:
            pass
        
        return None
    
    def extract_from_multiple_pages(self, html_pages: dict, default_country: str = 'US') -> List[str]:
        """
        Extract phone numbers from multiple HTML pages.
        
        Args:
            html_pages: Dictionary of URL -> HTML content
            default_country: Default country code
        
        Returns:
            List of unique phone numbers
        """
        all_phones: Set[str] = set()
        
        for url, html in html_pages.items():
            phones = self.extract(html, default_country)
            all_phones.update(phones)
        
        return list(all_phones)
