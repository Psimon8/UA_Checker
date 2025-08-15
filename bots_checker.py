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
                'ip_ranges': [
                    '66.249.', '64.233.', '72.14.', '74.125.', '209.85.', '216.239.',
                    '172.217.', '108.177.', '142.250.', '172.253.'
                ],
                'dns_suffixes': ['.googlebot.com', '.google.com']
            },
            'bingbot': {
                'user_agent_pattern': r'bingbot',
                'ip_ranges': [
                    '65.52.', '131.253.', '157.54.', '157.55.', '207.46.',
                    '40.77.', '13.66.', '20.190.'
                ],
                'dns_suffixes': ['.search.msn.com']
            },
            'yandexbot': {
                'user_agent_pattern': r'yandexbot',
                'ip_ranges': [
                    '77.88.', '87.250.', '93.158.', '95.108.', '178.154.',
                    '141.8.', '199.21.'
                ],
                'dns_suffixes': ['.yandex.ru', '.yandex.com', '.yandex.net']
            },
            'facebookbot': {
                'user_agent_pattern': r'facebookexternalhit',
                'ip_ranges': ['31.13.', '66.220.', '69.63.', '69.171.', '74.119.', '173.252.'],
                'dns_suffixes': ['.facebook.com']
            },
            'twitterbot': {
                'user_agent_pattern': r'twitterbot',
                'ip_ranges': ['199.16.', '199.59.'],
                'dns_suffixes': ['.twitter.com']
            },
            'linkedinbot': {
                'user_agent_pattern': r'linkedinbot',
                'ip_ranges': ['108.174.'],
                'dns_suffixes': ['.linkedin.com']
            },
            'openai': {
                'user_agent_pattern': r'gptbot|chatgpt-user|openai',
                'ip_ranges': ['20.15.', '40.83.', '52.230.', '20.171.'],
                'dns_suffixes': ['.openai.com']
            },
            'anthropic': {
                'user_agent_pattern': r'claude-bot|anthropic',
                'ip_ranges': ['54.186.', '52.40.', '35.160.', '3.101.'],
                'dns_suffixes': ['.anthropic.com']
            },
            'perplexity': {
                'user_agent_pattern': r'perplexitybot',
                'ip_ranges': ['3.91.', '34.205.', '52.87.', '44.192.'],
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
    
    def check_user_agent(self, user_agent: str) -> Dict:
        """Vérifie le user agent contre les patterns de bots connus"""
        user_agent_lower = user_agent.lower()
        detected_bots = []
        
        for bot_name, bot_info in self.known_bots.items():
            pattern = bot_info['user_agent_pattern']
            if re.search(pattern, user_agent_lower, re.IGNORECASE):
                detected_bots.append(bot_name)
        
        return {
            'detected_bots': detected_bots,
            'is_bot': len(detected_bots) > 0,
            'user_agent': user_agent
        }
    
    def check_ip_range(self, ip: str, bot_name: str) -> bool:
        """Vérifie si l'IP appartient aux ranges du bot spécifié"""
        if bot_name not in self.known_bots:
            return False
        
        ip_ranges = self.known_bots[bot_name]['ip_ranges']
        return any(ip.startswith(ip_range) for ip_range in ip_ranges)
    
    def check_reverse_dns(self, ip: str, bot_name: str) -> Dict:
        """Vérifie la résolution DNS inverse pour valider l'authenticité du bot"""
        try:
            # Résolution DNS inverse
            hostname = socket.gethostbyaddr(ip)[0].lower()
            
            # Vérification du suffixe DNS
            if bot_name in self.known_bots:
                dns_suffixes = self.known_bots[bot_name]['dns_suffixes']
                is_valid_dns = any(hostname.endswith(suffix) for suffix in dns_suffixes)
            else:
                is_valid_dns = False
            
            # Vérification DNS directe (forward lookup)
            try:
                resolved_ip = socket.gethostbyname(hostname)
                dns_matches = resolved_ip == ip
            except socket.gaierror:
                dns_matches = False
            
            return {
                'hostname': hostname,
                'is_valid_dns': is_valid_dns,
                'dns_matches': dns_matches,
                'is_authentic': is_valid_dns and dns_matches
            }
        
        except socket.herror:
            return {
                'hostname': None,
                'is_valid_dns': False,
                'dns_matches': False,
                'is_authentic': False,
                'error': 'No reverse DNS record found'
            }
        except Exception as e:
            return {
                'hostname': None,
                'is_valid_dns': False,
                'dns_matches': False,
                'is_authentic': False,
                'error': str(e)
            }
    
    def comprehensive_check(self, user_agent: str, ip: str) -> Dict:
        """Effectue une vérification complète du bot"""
        # Vérification du user agent
        ua_result = self.check_user_agent(user_agent)
        
        results = {
            'user_agent': user_agent,
            'ip': ip,
            'timestamp': datetime.now().isoformat(),
            'detected_bots': ua_result['detected_bots'],
            'is_bot_claimed': ua_result['is_bot'],
            'bot_validations': {}
        }
        
        # Pour chaque bot détecté, effectuer une validation complète
        for bot_name in ua_result['detected_bots']:
            # Vérification de l'IP
            ip_valid = self.check_ip_range(ip, bot_name)
            
            # Vérification DNS
            dns_result = self.check_reverse_dns(ip, bot_name)
            
            # Détermination de la légitimité
            is_legitimate = ip_valid or dns_result.get('is_authentic', False)
            
            results['bot_validations'][bot_name] = {
                'ip_range_valid': ip_valid,
                'dns_validation': dns_result,
                'is_legitimate': is_legitimate,
                'confidence': 'high' if (ip_valid and dns_result.get('is_authentic', False)) else 
                            'medium' if (ip_valid or dns_result.get('is_authentic', False)) else 'low'
            }
        
        # Résumé global
        legitimate_bots = [bot for bot, validation in results['bot_validations'].items() 
                          if validation['is_legitimate']]
        
        results['summary'] = {
            'is_legitimate_bot': len(legitimate_bots) > 0,
            'legitimate_bots': legitimate_bots,
            'suspicious': ua_result['is_bot'] and len(legitimate_bots) == 0,
            'verdict': self._get_verdict(ua_result['is_bot'], len(legitimate_bots))
        }
        
        return results
    
    def _get_verdict(self, claims_bot: bool, legitimate_count: int) -> str:
        """Détermine le verdict final"""
        if not claims_bot:
            return "human_user"
        elif legitimate_count > 0:
            return "legitimate_bot"
        else:
            return "suspicious_bot"
    
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
    
    def batch_check_bots(self, bot_data: List[Dict]) -> List[Dict]:
        """Vérifie plusieurs bots en lot"""
        results = []
        
        for data in bot_data:
            user_agent = data.get('user_agent', '')
            ip = data.get('ip', '')
            
            if user_agent and ip:
                result = self.comprehensive_check(user_agent, ip)
                results.append(result)
        
        return results
    
    def export_to_excel(self, results: List[Dict], filename: str = None, export_type: str = 'robots') -> str:
        """Exporte les résultats vers Excel"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{export_type}_check_{timestamp}.xlsx"
        
        if export_type == 'robots':
            data = self._format_robots_data(results)
        else:
            data = self._format_bot_validation_data(results)
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        return filename
    
    def _format_robots_data(self, results: List[Dict]) -> List[Dict]:
        """Formate les données pour l'export robots.txt"""
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
        return data
    
    def _format_bot_validation_data(self, results: List[Dict]) -> List[Dict]:
        """Formate les données pour l'export de validation de bots"""
        data = []
        for result in results:
            base_row = {
                'User_Agent': result.get('user_agent', ''),
                'IP': result.get('ip', ''),
                'Timestamp': result.get('timestamp', ''),
                'Claims_Bot': result.get('is_bot_claimed', False),
                'Verdict': result.get('summary', {}).get('verdict', ''),
                'Is_Legitimate': result.get('summary', {}).get('is_legitimate_bot', False),
                'Is_Suspicious': result.get('summary', {}).get('suspicious', False),
                'Legitimate_Bots': '; '.join(result.get('summary', {}).get('legitimate_bots', []))
            }
            
            if result.get('bot_validations'):
                for bot_name, validation in result['bot_validations'].items():
                    row = base_row.copy()
                    row.update({
                        'Detected_Bot': bot_name,
                        'IP_Range_Valid': validation.get('ip_range_valid', False),
                        'DNS_Hostname': validation.get('dns_validation', {}).get('hostname', ''),
                        'DNS_Valid': validation.get('dns_validation', {}).get('is_valid_dns', False),
                        'DNS_Matches': validation.get('dns_validation', {}).get('dns_matches', False),
                        'DNS_Authentic': validation.get('dns_validation', {}).get('is_authentic', False),
                        'Confidence': validation.get('confidence', 'low')
                    })
                    data.append(row)
            else:
                base_row.update({
                    'Detected_Bot': '',
                    'IP_Range_Valid': False,
                    'DNS_Hostname': '',
                    'DNS_Valid': False,
                    'DNS_Matches': False,
                    'DNS_Authentic': False,
                    'Confidence': 'low'
                })
                data.append(base_row)
        
        return data

def main():
    checker = BotsChecker()
    
    # Exemple d'utilisation - cas de test
    test_cases = [
        {
            'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'ip': '66.249.66.1'
        },
        {
            'user_agent': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'ip': '65.52.1.1'
        },
        {
            'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'ip': '192.168.1.1'  # IP suspecte pour Googlebot
        }
    ]
    
    print("=== Bot Checker - Validation des bots ===\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"User Agent: {case['user_agent']}")
        print(f"IP: {case['ip']}")
        
        result = checker.comprehensive_check(case['user_agent'], case['ip'])
        
        print(f"Verdict: {result['summary']['verdict']}")
        print(f"Is Legitimate: {result['summary']['is_legitimate_bot']}")
        print(f"Is Suspicious: {result['summary']['suspicious']}")
        
        if result['bot_validations']:
            print("\nBot Validations:")
            for bot_name, validation in result['bot_validations'].items():
                print(f"  {bot_name}:")
                print(f"    - IP Range Valid: {validation['ip_range_valid']}")
                print(f"    - DNS Authentic: {validation['dns_validation'].get('is_authentic', False)}")
                print(f"    - Confidence: {validation['confidence']}")
        
        print("-" * 60)

if __name__ == "__main__":
    main()
