"""
Module de test d'accès des bots
"""

import time
import requests
from typing import Dict, List
from datetime import datetime

from .html_parser import HTMLParser
from .robots_parser import RobotsParser


class BotTester:
    """Gestionnaire pour les tests d'accès des bots"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.robots_parser = RobotsParser()
        self.html_parser = HTMLParser()
    
    def test_bot_access(self, url: str, bot_name: str, user_agent_name: str, 
                       user_agent: str, robots_parser) -> Dict:
        """Test d'accès pour un user agent spécifique"""
        try:
            # Vérifier robots.txt
            robots_allowed = self.robots_parser.check_robots_permission(robots_parser, user_agent, url)
            
            # Test d'accès HTTP
            headers = {'User-Agent': user_agent}
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=self.timeout)
            load_time = time.time() - start_time
            
            # Parser le HTML
            title, robots_meta, has_noindex = self.html_parser.parse_html(response.text)
            
            # Calculer is_allowed: statut 200 + robots.txt autorise + pas de noindex
            is_allowed = (response.status_code == 200 and robots_allowed and not has_noindex)
            
            # Déterminer le statut final
            if is_allowed:
                status = 'OK'
                reason = 'Accès autorisé'
            else:
                status = 'KO'
                reasons = []
                if response.status_code != 200:
                    reasons.append(f'HTTP {response.status_code}')
                if not robots_allowed:
                    reasons.append('Robots.txt bloque')
                if has_noindex:
                    reasons.append('Meta noindex')
                reason = ', '.join(reasons) if reasons else 'Bloqué'
            
            return {
                'bot_name': bot_name,
                'user_agent_name': user_agent_name,
                'user_agent': user_agent,
                'status': status,
                'reason': reason,
                'status_code': response.status_code,
                'robots_allowed': robots_allowed,
                'robots_meta': robots_meta,
                'has_noindex': has_noindex,
                'title': title,
                'load_time': round(load_time, 2),
                'is_allowed': is_allowed
            }
            
        except requests.exceptions.Timeout:
            return self._create_error_result(bot_name, user_agent_name, user_agent, 
                                           'NA', 'Timeout', 408, robots_parser, url)
        except requests.exceptions.RequestException as e:
            return self._create_error_result(bot_name, user_agent_name, user_agent, 
                                           'NA', f'Erreur réseau: {str(e)[:50]}', 0, 
                                           robots_parser, url)
    
    def _create_error_result(self, bot_name: str, user_agent_name: str, user_agent: str,
                           status: str, reason: str, status_code: int, 
                           robots_parser, url: str) -> Dict:
        """Crée un résultat d'erreur standardisé"""
        return {
            'bot_name': bot_name,
            'user_agent_name': user_agent_name,
            'user_agent': user_agent,
            'status': status,
            'reason': reason,
            'status_code': status_code,
            'robots_allowed': self.robots_parser.check_robots_permission(robots_parser, user_agent, url),
            'robots_meta': 'Erreur' if status_code != 408 else 'Timeout',
            'has_noindex': False,
            'title': 'Erreur' if status_code != 408 else 'Timeout',
            'load_time': self.timeout if status_code == 408 else 0,
            'is_allowed': False
        }
    
    def determine_bot_status(self, bot_tests: List[Dict]) -> tuple:
        """Détermine le statut global d'un bot basé sur ses tests"""
        if not bot_tests:
            return 'NA', 'Aucun test effectué'
        
        ok_count = sum(1 for test in bot_tests if test['status'] == 'OK')
        ko_count = sum(1 for test in bot_tests if test['status'] == 'KO')
        na_count = sum(1 for test in bot_tests if test['status'] == 'NA')
        
        if ok_count > 0:
            # Au moins un UA fonctionne
            if ko_count == 0 and na_count == 0:
                return 'OK', 'Tous les UA autorisés'
            else:
                return 'OK', f'{ok_count}/{len(bot_tests)} UA autorisés'
        elif na_count == len(bot_tests):
            # Tous les tests impossibles
            return 'NA', 'Tous les tests impossibles'
        else:
            # Tous bloqués ou mix de KO/NA
            if ko_count == len(bot_tests):
                return 'KO', 'Tous les UA bloqués'
            else:
                return 'KO', f'{ko_count} bloqués, {na_count} impossibles'
