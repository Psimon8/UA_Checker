"""
Module de parsing HTML pour extraire les informations des pages
"""

import re
from typing import Tuple

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class HTMLParser:
    """Gestionnaire pour le parsing HTML"""
    
    @staticmethod
    def parse_html(html_content: str) -> Tuple[str, str, bool]:
        """Parse le HTML pour extraire titre, meta robots et noindex"""
        if not BeautifulSoup:
            return HTMLParser._parse_html_fallback(html_content)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else 'No title'
            
            robots_tag = soup.find('meta', attrs={'name': 'robots'})
            robots_content = robots_tag.get('content', '').strip() if robots_tag else ''
            
            if not robots_content:
                robots_meta = 'No robots meta'
                has_noindex = False
            else:
                robots_meta = robots_content
                has_noindex = 'noindex' in robots_content.lower()
            
            return title, robots_meta, has_noindex
        except Exception:
            return 'Parse error', 'Parse error', False
    
    @staticmethod
    def _parse_html_fallback(html_content: str) -> Tuple[str, str, bool]:
        """Fallback simple sans BeautifulSoup"""
        try:
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else 'No title'
            
            robots_match = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            robots_content = robots_match.group(1) if robots_match else ''
            
            if not robots_content:
                robots_meta = 'No robots meta'
                has_noindex = False
            else:
                robots_meta = robots_content
                has_noindex = 'noindex' in robots_content.lower()
            
            return title, robots_meta, has_noindex
        except Exception:
            return 'Parse error', 'Parse error', False
