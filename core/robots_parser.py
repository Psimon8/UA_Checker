"""
Module de parsing et vérification des robots.txt
"""

import requests
from urllib.parse import urlparse
from typing import Optional, Tuple

try:
    from protego import Protego
except ImportError:
    Protego = None


class RobotsParser:
    """Gestionnaire pour le parsing des robots.txt"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def get_robots_parser(self, url: str) -> Tuple[Optional[object], Optional[str]]:
        """Récupère et parse le robots.txt avec Protego"""
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            response = requests.get(robots_url, timeout=self.timeout)
            if response.status_code == 200 and Protego:
                return Protego.parse(response.text), robots_url
            return None, robots_url
        except Exception:
            return None, None
    
    def check_robots_permission(self, robots_parser, user_agent: str, url: str) -> bool:
        """Vérifie la permission robots.txt avec Protego"""
        if not robots_parser:
            return True  # Pas de robots.txt = autorisé
        
        try:
            return robots_parser.can_fetch(url, user_agent)
        except Exception:
            return False  # Erreur de parsing = bloqué par sécurité
    
    def is_blocked_by_robots(self, url: str, bot_rules: dict) -> bool:
        """Détermine si une URL est bloquée par robots.txt"""
        parsed_url = urlparse(url)
        path = parsed_url.path or '/'
        
        disallowed = bot_rules.get('disallowed', [])
        allowed = bot_rules.get('allowed', [])
        
        # Vérifier les règles Allow d'abord (priorité)
        for allow_rule in allowed:
            if path.startswith(allow_rule):
                return False
        
        # Vérifier les règles Disallow
        for disallow_rule in disallowed:
            if disallow_rule == '/':
                return True
            elif path.startswith(disallow_rule):
                return True
        
        return False
