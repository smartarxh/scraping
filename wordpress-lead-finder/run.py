#!/usr/bin/env python3
"""
WordPress Lead Finder - Entry Point

Run this file to start the web interface.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.web_interface import app

if __name__ == '__main__':
    print("=" * 50)
    print("       WORDPRESS LEAD FINDER")
    print("=" * 50)
    print("\nStarting web interface...")
    print("Open http://localhost:5000 in your browser\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
