import requests
import re
import socket
import json
from urllib.parse import urlparse
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import time
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

class BotsChecker:
    def __init__(self):
        self.known_bots = {
            'googlebot': {
                'user_agent_pattern': r'googlebot',
                'user_agents': [
                    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/W.X.Y.Z Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Googlebot/2.1 (+http://www.google.com/bot.html)',
                    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36'
                ],
                'ip_ranges': [
                    '66.249.', '64.233.', '72.14.', '74.125.', '209.85.', '216.239.',
                    '172.217.', '108.177.', '142.250.', '172.253.'
                ],
                'dns_suffixes': ['.googlebot.com', '.google.com']
            },
            'bingbot': {
                'user_agent_pattern': r'bingbot',
                'user_agents': [
                    'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/W.X.Y.Z Safari/537.36',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
                ],
                'ip_ranges': [
                    '65.52.', '131.253.', '157.54.', '157.55.', '207.46.',
                    '40.77.', '13.66.', '20.190.'
                ],
                'dns_suffixes': ['.search.msn.com']
            },
            'yandexbot': {
                'user_agent_pattern': r'yandexbot',
                'user_agents': [
                    'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B411 Safari/600.1.4 (compatible; YandexMobileBot/3.0; +http://yandex.com/bots)'
                ],
                'ip_ranges': [
                    '77.88.', '87.250.', '93.158.', '95.108.', '178.154.',
                    '141.8.', '199.21.'
                ],
                'dns_suffixes': ['.yandex.ru', '.yandex.com', '.yandex.net']
            },
            'facebookbot': {
                'user_agent_pattern': r'facebookexternalhit',
                'user_agents': [
                    'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
                    'facebookexternalhit/1.1',
                    'Mozilla/5.0 (compatible; FacebookBot/1.0; +https://developers.facebook.com/docs/sharing/webmasters/crawler)'
                ],
                'ip_ranges': ['31.13.', '66.220.', '69.63.', '69.171.', '74.119.', '173.252.'],
                'dns_suffixes': ['.facebook.com']
            },
            'twitterbot': {
                'user_agent_pattern': r'twitterbot',
                'user_agents': [
                    'Twitterbot/1.0',
                    'Mozilla/5.0 (compatible; Twitterbot/1.0)'
                ],
                'ip_ranges': ['199.16.', '199.59.'],
                'dns_suffixes': ['.twitter.com']
            },
            'linkedinbot': {
                'user_agent_pattern': r'linkedinbot',
                'user_agents': [
                    'LinkedInBot/1.0 (compatible; Mozilla/5.0; +http://www.linkedin.com/)',
                    'Mozilla/5.0 (compatible; LinkedInBot/1.0; +http://www.linkedin.com/)'
                ],
                'ip_ranges': ['108.174.'],
                'dns_suffixes': ['.linkedin.com']
            },
            'openai': {
                'user_agent_pattern': r'gptbot|chatgpt-user|openai',
                'user_agents': [
                    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.0; +https://openai.com/gptbot',
                    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot',
                    'GPTBot/1.0; +https://openai.com/gptbot'
                ],
                'ip_ranges': ['20.15.', '40.83.', '52.230.', '20.171.'],
                'dns_suffixes': ['.openai.com']
            },
            'anthropic': {
                'user_agent_pattern': r'claude-bot|anthropic',
                'user_agents': [
                    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; Claude-Bot/1.0; +https://www.anthropic.com/',
                    'Claude-Bot/1.0; +https://www.anthropic.com/'
                ],
                'ip_ranges': ['54.186.', '52.40.', '35.160.', '3.101.'],
                'dns_suffixes': ['.anthropic.com']
            },
            'perplexity': {
                'user_agent_pattern': r'perplexitybot',
                'user_agents': [
                    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; PerplexityBot/1.0; +https://www.perplexity.ai/',
                    'PerplexityBot/1.0; +https://www.perplexity.ai/'
                ],
                'ip_ranges': ['3.91.', '34.205.', '52.87.', '44.192.'],
                'dns_suffixes': ['.perplexity.ai']
            },
            'cohere': {
                'user_agent_pattern': r'cohere-ai',
                'user_agents': [
                    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; Cohere-AI/1.0',
                    'Cohere-AI/1.0'
                ],
                'ip_ranges': ['35.236.', '34.102.', '35.224.'],
                'dns_suffixes': ['.cohere.ai']
            },
            'meta': {
                'user_agent_pattern': r'meta-externalagent',
                'user_agents': [
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0',
                    'Meta-ExternalAgent/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/crawler)'
                ],
                'ip_ranges': ['31.13.', '66.220.', '69.63.', '69.171.', '74.119.', '173.252.'],
                'dns_suffixes': ['.facebook.com', '.meta.com']
            },
            'applebot': {
                'user_agent_pattern': r'applebot',
                'user_agents': [
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15 (Applebot/0.1; +http://www.apple.com/go/applebot)',
                    'Mozilla/5.0 (Device; OS X.Y) AppleWebKit/WebKit Version Safari/Safari Version (Applebot/0.1; +http://www.apple.com/go/applebot)'
                ],
                'ip_ranges': ['17.', '23.', '63.92.'],
                'dns_suffixes': ['.apple.com']
            },
            'baiduspider': {
                'user_agent_pattern': r'baiduspider',
                'user_agents': [
                    'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1 (compatible; Baiduspider-render/2.0; +http://www.baidu.com/search/spider.html)'
                ],
                'ip_ranges': ['220.181.', '123.125.', '180.76.'],
                'dns_suffixes': ['.baidu.com', '.baidu.jp']
            }
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BotsChecker/1.0 (+https://github.com/bots-checker)'
        })
    
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
    
    def check_url_access(self, url: str, bot_name: str = None, user_agent: str = None) -> Dict:
        """Vérifie l'accès à une URL avec simulation de bot"""
        try:
            start_time = time.time()
            
            # Headers personnalisés si un bot spécifique est testé
            headers = {}
            if user_agent:
                headers['User-Agent'] = user_agent
            elif bot_name and bot_name in self.known_bots:
                # User agents par défaut pour les bots
                default_agents = {
                    'googlebot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'bingbot': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                    'openai': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.0; +https://openai.com/gptbot'
                }
                if bot_name in default_agents:
                    headers['User-Agent'] = default_agents[bot_name]
            
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            load_time = time.time() - start_time
            
            # Analyse du contenu HTML pour robots meta
            robots_meta = self._extract_robots_meta(response.text)
            
            # Extraction du titre
            title = self._extract_title(response.text)
            
            return {
                'url': url,
                'status_code': response.status_code,
                'status_text': self._get_status_text(response.status_code),
                'load_time': round(load_time, 2),
                'title': title,
                'robots_meta': robots_meta,
                'headers': dict(response.headers),
                'success': response.status_code < 400
            }
            
        except requests.exceptions.Timeout:
            return {
                'url': url,
                'status_code': 408,
                'status_text': 'Timeout',
                'load_time': 10.0,
                'title': 'Request Timeout',
                'robots_meta': 'No robots meta',
                'error': 'Request timeout',
                'success': False
            }
        except Exception as e:
            return {
                'url': url,
                'status_code': 0,
                'status_text': 'Error',
                'load_time': 0,
                'title': 'Error',
                'robots_meta': 'No robots meta',
                'error': str(e),
                'success': False
            }
    
    def _extract_robots_meta(self, html_content: str) -> str:
        """Extrait les balises meta robots du HTML"""
        if not BeautifulSoup:
            # Fallback sans BeautifulSoup
            try:
                import re
                meta_pattern = r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)["\'][^>]*>'
                matches = re.findall(meta_pattern, html_content, re.IGNORECASE)
                return ', '.join(matches) if matches else 'No robots meta'
            except:
                return 'No robots meta'
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            robots_tags = soup.find_all('meta', attrs={'name': re.compile(r'robots', re.I)})
            
            if not robots_tags:
                return 'No robots meta'
            
            robot_directives = []
            for tag in robots_tags:
                content = tag.get('content', '').strip()
                if content:
                    robot_directives.append(content)
            
            return ', '.join(robot_directives) if robot_directives else 'No robots meta'
        except:
            return 'No robots meta'
    
    def _extract_title(self, html_content: str) -> str:
        """Extrait le titre de la page HTML"""
        if not BeautifulSoup:
            # Fallback sans BeautifulSoup
            try:
                import re
                title_pattern = r'<title[^>]*>([^<]+)</title>'
                match = re.search(title_pattern, html_content, re.IGNORECASE | re.DOTALL)
                return match.group(1).strip() if match else 'No title'
            except:
                return 'No title'
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.get_text().strip() if title_tag else 'No title'
        except:
            return 'No title'
    
    def _get_status_text(self, status_code: int) -> str:
        """Retourne le texte correspondant au code de statut"""
        status_texts = {
            200: 'OK',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error',
            408: 'Timeout',
            0: 'Connection Error'
        }
        return status_texts.get(status_code, f'HTTP {status_code}')
    
    def check_bot_access(self, url: str, bot_name: str) -> Dict:
        """Vérifie l'accès complet d'un bot à une URL (robots.txt + accès direct)"""
        try:
            # Vérification robots.txt
            robots_result = self.check_robots_txt(url, [bot_name])
            
            # Vérification de l'accès direct
            access_result = self.check_url_access(url, bot_name)
            
            # Analyse des résultats robots.txt
            robots_status = 'Unknown'
            if 'error' not in robots_result and 'results' in robots_result:
                bot_rules = robots_result['results'].get(bot_name, {})
                if bot_rules.get('disallowed'):
                    # Vérifier si l'URL est explicitement bloquée
                    parsed_url = urlparse(url)
                    path = parsed_url.path or '/'
                    
                    is_blocked = False
                    for disallow_pattern in bot_rules['disallowed']:
                        if disallow_pattern == '/' or path.startswith(disallow_pattern):
                            is_blocked = True
                            break
                    
                    robots_status = 'Blocked' if is_blocked else 'Allowed'
                else:
                    robots_status = 'Allowed'
            else:
                robots_status = 'No robots.txt'
            
            # Détermination du statut global
            if access_result['status_code'] == 403:
                overall_status = 'BLOCKED'
            elif access_result['status_code'] == 200:
                overall_status = 'ALLOWED'
            else:
                overall_status = 'ERROR'
            
            return {
                'bot_name': bot_name.upper(),
                'url': url,
                'overall_status': overall_status,
                'status_code': access_result['status_code'],
                'robots_meta': access_result['robots_meta'],
                'robots_txt': robots_status,
                'title': access_result['title'],
                'load_time': f"{access_result['load_time']}s",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'bot_name': bot_name.upper(),
                'url': url,
                'overall_status': 'ERROR',
                'status_code': 0,
                'robots_meta': 'No robots meta',
                'robots_txt': 'Error',
                'title': 'Error',
                'load_time': '0s',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_url_access_detailed(self, url: str, bot_name: str) -> Dict:
        """Test détaillé d'accès avec multiple User-Agents pour un bot"""
        bot_info = self.known_bots.get(bot_name, {})
        user_agents = bot_info.get('user_agents', [])
        
        if not user_agents:
            return {
                'bot_name': bot_name.upper(),
                'url': url,
                'status': 'NA',
                'reason': 'Aucun User-Agent configuré',
                'details': []
            }
        
        test_results = []
        overall_status = 'OK'  # Par défaut OK
        blocking_reasons = []
        
        for i, user_agent in enumerate(user_agents):
            try:
                start_time = time.time()
                headers = {'User-Agent': user_agent}
                
                response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                load_time = round(time.time() - start_time, 2)
                
                # Analyser la réponse
                test_result = {
                    'user_agent': user_agent,
                    'status_code': response.status_code,
                    'load_time': load_time,
                    'blocked': False,
                    'reason': ''
                }
                
                # Déterminer si c'est bloqué
                if response.status_code == 403:
                    test_result['blocked'] = True
                    test_result['reason'] = 'HTTP 403 Forbidden'
                    blocking_reasons.append(f'UA{i+1}: 403 Forbidden')
                elif response.status_code == 429:
                    test_result['blocked'] = True
                    test_result['reason'] = 'HTTP 429 Too Many Requests'
                    blocking_reasons.append(f'UA{i+1}: 429 Rate Limited')
                elif response.status_code == 406:
                    test_result['blocked'] = True
                    test_result['reason'] = 'HTTP 406 Not Acceptable'
                    blocking_reasons.append(f'UA{i+1}: 406 Not Acceptable')
                elif 400 <= response.status_code < 500:
                    test_result['blocked'] = True
                    test_result['reason'] = f'HTTP {response.status_code}'
                    blocking_reasons.append(f'UA{i+1}: {response.status_code}')
                elif response.status_code >= 500:
                    # Erreur serveur = NA, pas de blocage
                    test_result['reason'] = f'Erreur serveur {response.status_code}'
                else:
                    test_result['reason'] = f'Succès {response.status_code}'
                
                test_results.append(test_result)
                
            except requests.exceptions.Timeout:
                test_results.append({
                    'user_agent': user_agent,
                    'status_code': 408,
                    'load_time': 15.0,
                    'blocked': False,
                    'reason': 'Timeout'
                })
                
            except requests.exceptions.ConnectionError:
                test_results.append({
                    'user_agent': user_agent,
                    'status_code': 0,
                    'load_time': 0,
                    'blocked': False,
                    'reason': 'Connection Error'
                })
                
            except Exception as e:
                test_results.append({
                    'user_agent': user_agent,
                    'status_code': 0,
                    'load_time': 0,
                    'blocked': False,
                    'reason': f'Error: {str(e)}'
                })
        
        # Déterminer le statut global
        blocked_count = sum(1 for result in test_results if result['blocked'])
        error_count = sum(1 for result in test_results if result['status_code'] == 0 or result['status_code'] >= 500)
        timeout_count = sum(1 for result in test_results if 'Timeout' in result['reason'])
        
        if blocked_count == len(test_results):
            overall_status = 'KO'
            reason = f'Tous les UA bloqués ({", ".join(blocking_reasons)})'
        elif blocked_count > 0:
            if blocked_count >= len(test_results) / 2:
                overall_status = 'KO'
                reason = f'{blocked_count}/{len(test_results)} UA bloqués ({", ".join(blocking_reasons)})'
            else:
                overall_status = 'OK'
                reason = f'Partiellement bloqué: {blocked_count}/{len(test_results)} UA'
        elif error_count == len(test_results) or timeout_count == len(test_results):
            overall_status = 'NA'
            reason = 'Impossible de tester (erreurs/timeouts)'
        else:
            overall_status = 'OK'
            reason = 'Accès autorisé'
        
        return {
            'bot_name': bot_name.upper(),
            'url': url,
            'status': overall_status,
            'reason': reason,
            'details': test_results,
            'summary': {
                'total_tests': len(test_results),
                'blocked': blocked_count,
                'errors': error_count,
                'timeouts': timeout_count,
                'success': len(test_results) - blocked_count - error_count
            }
        }

    def check_robots_txt_advanced(self, url: str, selected_bots: List[str]) -> Dict:
        """Vérification avancée robots.txt avec tests d'accès détaillés"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            # Vérifier robots.txt
            try:
                response = requests.get(robots_url, timeout=10)
                robots_available = response.status_code == 200
                robots_content = response.text if robots_available else ""
            except:
                robots_available = False
                robots_content = ""
            
            results = {}
            
            for bot in selected_bots:
                # Analyser robots.txt
                if robots_available:
                    bot_rules = self._parse_robots_for_bot(robots_content, bot)
                else:
                    bot_rules = {'allowed': [], 'disallowed': [], 'crawl_delay': None}
                
                # Test d'accès réel
                access_test = self.check_url_access_detailed(url, bot)
                
                # Déterminer le statut final
                robots_blocked = self._is_blocked_by_robots(url, bot_rules)
                
                final_status = 'OK'
                final_reason = []
                
                # Logique de décision améliorée
                if access_test['status'] == 'KO':
                    final_status = 'KO'
                    final_reason.append(f"Accès bloqué: {access_test['reason']}")
                elif access_test['status'] == 'NA':
                    if robots_blocked:
                        final_status = 'KO'
                        final_reason.append("Bloqué par robots.txt")
                    else:
                        final_status = 'NA'
                        final_reason.append("Test impossible")
                elif robots_blocked:
                    # Accès OK mais robots.txt dit non - priorité à l'accès réel
                    final_status = 'OK'
                    final_reason.append("Autorisé malgré robots.txt")
                else:
                    final_status = 'OK'
                    final_reason.append("Accès autorisé")
                
                results[bot] = {
                    'status': final_status,
                    'reason': ' | '.join(final_reason),
                    'robots_txt': bot_rules,
                    'robots_blocked': robots_blocked,
                    'access_test': access_test,
                    'robots_available': robots_available
                }
            
            return {
                'url': robots_url,
                'original_url': url,
                'status': 'success',
                'robots_available': robots_available,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'url': url,
                'original_url': url,
                'error': f'Erreur lors de la vérification: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

    def _is_blocked_by_robots(self, url: str, bot_rules: Dict) -> bool:
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

    # Mise à jour de la méthode check_robots_txt pour utiliser la version avancée
    def check_robots_txt(self, url: str, selected_bots: List[str]) -> Dict:
        """Méthode mise à jour utilisant les tests avancés"""
        return self.check_robots_txt_advanced(url, selected_bots)

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
    
    # Test spécifique pour OpenAI GPTBot
    test_url = "https://example.com"  # Remplacer par l'URL à tester
    
    print("=== Bot Access Checker ===\n")
    
    # Test OpenAI GPTBot
    result = checker.check_bot_access(test_url, 'openai')
    formatted_output = checker.format_result_output(result)
    print(formatted_output)
    
    print("\n" + "="*50 + "\n")
    
    # Tests supplémentaires
    test_bots = ['googlebot', 'bingbot', 'openai']
    
    for bot in test_bots:
        result = checker.check_bot_access(test_url, bot)
        formatted_output = checker.format_result_output(result)
        print(formatted_output)
        print()

if __name__ == "__main__":
    main()
