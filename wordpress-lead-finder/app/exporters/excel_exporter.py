"""
Excel exporter module
Exports leads to Excel format
"""

import os
from typing import List, Dict
import pandas as pd


class ExcelExporter:
    """
    Exports leads to Excel (.xlsx) format.
    """
    
    def __init__(self):
        self.columns = [
            'Business Name',
            'Website URL',
            'Domain',
            'CMS',
            'WordPress Confidence',
            'Email',
            'Phone',
            'Contact Page',
            'Search Keyword',
            'Source',
            'Date Found'
        ]
    
    def export(self, leads: List[Dict], output_path: str) -> bool:
        """
        Export leads to Excel file.
        
        Args:
            leads: List of lead dictionaries
            output_path: Path to output file
        
        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert to DataFrame
            df = pd.DataFrame(leads, columns=self.columns)
            
            # Write to Excel
            df.to_excel(output_path, index=False, sheet_name='Leads')
            
            return True
        
        except Exception as e:
            print(f"Excel export error: {e}")
            return False
    
    def create_lead_dict(
        self,
        business_name: str,
        website_url: str,
        domain: str,
        cms: str,
        wp_confidence: int,
        email: str,
        phone: str,
        contact_page: str,
        keyword: str,
        source: str,
        date_found: str
    ) -> Dict:
        """
        Create a lead dictionary with all required fields.
        """
        return {
            'Business Name': business_name,
            'Website URL': website_url,
            'Domain': domain,
            'CMS': cms,
            'WordPress Confidence': wp_confidence,
            'Email': email,
            'Phone': phone,
            'Contact Page': contact_page,
            'Search Keyword': keyword,
            'Source': source,
            'Date Found': date_found
        }
