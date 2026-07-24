"""
Logging utility for WordPress Lead Finder
"""

import logging
import os
from datetime import datetime


def setup_logger(log_file: str = None, level: str = 'INFO') -> logging.Logger:
    """
    Setup and return a logger instance.
    
    Args:
        log_file: Path to log file (optional)
        level: Logging level
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger('wordpress_lead_finder')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if log_file provided)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def create_job_logger(output_dir: str, keyword: str) -> logging.Logger:
    """
    Create a logger for a specific job (keyword search).
    
    Args:
        output_dir: Base output directory
        keyword: Search keyword
    
    Returns:
        Logger instance
    """
    # Sanitize keyword for filename
    safe_keyword = sanitize_filename(keyword)
    log_file = os.path.join(output_dir, safe_keyword, f"{safe_keyword}.log")
    
    return setup_logger(log_file)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename.
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()
