import requests
import re
import socket
import json
from urllib.parse import urlparse
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

class BotsChecker:
    def __init__(self):
        self.known_bots = {
            'googlebot': {
                'user_agent_pattern': r'googlebot',
                'ip_ranges': ['66.249.', '64.233.', '72.14.', '74.125.', '209.85.', '216.239.'],
                'dns_suffixes': ['.googlebot.com', '.google.com']
            },
            'bingbot': {
                'user_agent_pattern': r'bingbot',
                'ip_ranges': ['65.52.', '131.253.', '157.54.', '157.55.', '207.46.'],
                'dns_suffixes': ['.search.msn.com']
            },
            'yandexbot': {
                'user_agent_pattern': r'yandexbot',
                'ip_ranges': ['77.88.', '87.250.', '93.158.', '95.108.', '178.154.'],
                'dns_suffixes': ['.yandex.ru', '.yandex.com']
            },
            'openai': {
                'user_agent_pattern': r'gptbot|chatgpt|openai',
                'ip_ranges': ['20.15.', '40.83.', '52.230.'],
                'dns_suffixes': ['.openai.com']
            },
            'anthropic': {
                'user_agent_pattern': r'claude-bot|anthropic',
                'ip_ranges': ['54.186.', '52.40.', '35.160.'],
                'dns_suffixes': ['.anthropic.com']
            },
            'perplexity': {
                'user_agent_pattern': r'perplexitybot',
                'ip_ranges': ['3.91.', '34.205.', '52.87.'],
                'dns_suffixes': ['.perplexity.ai']
            },
            'cohere': {
                'user_agent_pattern': r'cohere-ai',
                'ip_ranges': ['35.236.', '34.102.', '35.224.'],
                'dns_suffixes': ['.cohere.ai']
            }
        }
    
    def get_bot_list(self) -> List[str]:
        """Retourne la liste des bots disponibles"""
        return list(self.known_bots.keys())
    
    def check_robots_txt(self, url: str, selected_bots: List[str]) -> Dict:
        """Vérifie robots.txt pour les bots sélectionnés"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            response = requests.get(robots_url, timeout=10)
            if response.status_code != 200:
                return {'error': f'Impossible de récupérer robots.txt (HTTP {response.status_code})'}
            
            robots_content = response.text.lower()
            results = {}
            
            for bot in selected_bots:
                bot_rules = self._parse_robots_for_bot(robots_content, bot)
                results[bot] = bot_rules
            
            return {
                'url': robots_url,
                'status': 'success',
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Erreur lors de la vérification: {str(e)}'}
    
    def _parse_robots_for_bot(self, robots_content: str, bot: str) -> Dict:
        """Parse robots.txt pour un bot spécifique"""
        lines = robots_content.split('\n')
        current_agent = None
        bot_rules = {'allowed': [], 'disallowed': [], 'crawl_delay': None}
        
        bot_patterns = [bot.lower(), f'*{bot.lower()}*', '*']
        
        for line in lines:
            line = line.strip()
            if line.startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
            elif current_agent and any(pattern in current_agent for pattern in bot_patterns):
                if line.startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        bot_rules['disallowed'].append(path)
                elif line.startswith('allow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        bot_rules['allowed'].append(path)
                elif line.startswith('crawl-delay:'):
                    try:
                        bot_rules['crawl_delay'] = int(line.split(':', 1)[1].strip())
                    except ValueError:
                        pass
        
        return bot_rules
    
    def batch_check_urls(self, urls: List[str], selected_bots: List[str]) -> List[Dict]:
        """Vérifie plusieurs URLs"""
        results = []
        
        for url in urls:
            if not url.strip():
                continue
                
            url = url.strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            result = self.check_robots_txt(url, selected_bots)
            result['original_url'] = url
            results.append(result)
        
        return results
    
    def export_to_excel(self, results: List[Dict], filename: str = None) -> str:
        """Exporte les résultats vers Excel"""
        if filename is None:
            filename = f"robots_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        data = []
        for result in results:
            if 'error' in result:
                data.append({
                    'URL': result.get('original_url', ''),
                    'Status': 'Error',
                    'Error': result['error'],
                    'Bot': '',
                    'Allowed': '',
                    'Disallowed': '',
                    'Crawl_Delay': '',
                    'Timestamp': result.get('timestamp', '')
                })
            else:
                for bot, rules in result.get('results', {}).items():
                    data.append({
                        'URL': result['original_url'],
                        'Status': 'Success',
                        'Error': '',
                        'Bot': bot,
                        'Allowed': '; '.join(rules.get('allowed', [])),
                        'Disallowed': '; '.join(rules.get('disallowed', [])),
                        'Crawl_Delay': rules.get('crawl_delay', ''),
                        'Timestamp': result.get('timestamp', '')
                    })
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        return filename

def main():
    checker = BotsChecker()
    
    # Exemple d'utilisation
    test_cases = [
        {
            'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'ip': '66.249.66.1'
        },
        {
            'user_agent': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'ip': '65.52.1.1'
        }
    ]
    
    for case in test_cases:
        result = checker.comprehensive_check(case['user_agent'], case['ip'])
        print(f"User Agent: {case['user_agent'][:50]}...")
        print(f"IP: {case['ip']}")
        print(f"Result: {json.dumps(result, indent=2)}")
        print("-" * 50)

if __name__ == "__main__":
    main()
