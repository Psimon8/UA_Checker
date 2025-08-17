"""
Module principal pour la vérification des bots
"""

import requests
from typing import Dict, List
from datetime import datetime

from core.bot_definitions import BOT_DEFINITIONS
from core.robots_parser import RobotsParser
from core.bot_tester import BotTester


class BotsChecker:
    """Vérificateur principal des bots"""
    
    def __init__(self):
        self.known_bots = BOT_DEFINITIONS
        self.robots_parser = RobotsParser()
        self.bot_tester = BotTester()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BotsChecker/1.0 (+https://github.com/bots-checker)'
        })
    
    def get_bot_list(self) -> List[str]:
        """Retourne la liste des bots disponibles"""
        return list(self.known_bots.keys())
    
    def check_robots_txt(self, url: str, selected_bots: List[str]) -> Dict:
        """Vérification complète avec la nouvelle logique"""
        try:
            # Récupérer le parser robots.txt
            robots_parser, robots_url = self.robots_parser.get_robots_parser(url)
            
            results = {}
            all_tests = []
            
            for bot in selected_bots:
                if bot not in self.known_bots:
                    continue
                
                bot_info = self.known_bots[bot]
                user_agents = bot_info.get('user_agents', {})
                
                bot_tests = []
                
                # Tester chaque user agent du bot
                for ua_name, user_agent in user_agents.items():
                    test_result = self.bot_tester.test_bot_access(
                        url, bot, ua_name, user_agent, robots_parser
                    )
                    bot_tests.append(test_result)
                    all_tests.append(test_result)
                
                # Déterminer le statut global du bot
                bot_status, bot_reason = self.bot_tester.determine_bot_status(bot_tests)
                
                # Calculer le résumé
                ok_count = sum(1 for test in bot_tests if test['status'] == 'OK')
                ko_count = sum(1 for test in bot_tests if test['status'] == 'KO')
                na_count = sum(1 for test in bot_tests if test['status'] == 'NA')
                
                results[bot] = {
                    'status': bot_status,
                    'reason': bot_reason,
                    'tests': bot_tests,
                    'summary': {
                        'total': len(bot_tests),
                        'ok': ok_count,
                        'ko': ko_count,
                        'na': na_count
                    }
                }
            
            return {
                'url': robots_url if robots_url else url,
                'original_url': url,
                'status': 'success',
                'robots_available': robots_parser is not None,
                'results': results,
                'all_tests': all_tests,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'url': url,
                'original_url': url,
                'error': f'Erreur lors de la vérification: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }


if __name__ == "__main__":
    checker = BotsChecker()
    print("BotsChecker initialisé avec succès")
    print(f"Bots disponibles: {checker.get_bot_list()}")
    
    def get_bot_list(self) -> List[str]:
        """Retourne la liste des bots disponibles"""
        return list(self.known_bots.keys())

    def get_robots_parser(self, url: str):
        """Récupère et parse le robots.txt avec Protego"""
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            response = requests.get(robots_url, timeout=10)
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

    def parse_html(self, html_content: str) -> tuple:
        """Parse le HTML pour extraire titre, meta robots et noindex"""
        if not BeautifulSoup:
            # Fallback simple sans BeautifulSoup
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

    def test_bot_access(self, url: str, bot_name: str, user_agent_name: str, user_agent: str, robots_parser) -> Dict:
        """Test d'accès pour un user agent spécifique"""
        try:
            # Vérifier robots.txt
            robots_allowed = self.check_robots_permission(robots_parser, user_agent, url)
            
            # Test d'accès HTTP
            headers = {'User-Agent': user_agent}
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=30)
            load_time = time.time() - start_time
            
            # Parser le HTML
            title, robots_meta, has_noindex = self.parse_html(response.text)
            
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
            return {
                'bot_name': bot_name,
                'user_agent_name': user_agent_name,
                'user_agent': user_agent,
                'status': 'NA',
                'reason': 'Timeout',
                'status_code': 408,
                'robots_allowed': self.check_robots_permission(robots_parser, user_agent, url),
                'robots_meta': 'Timeout',
                'has_noindex': False,
                'title': 'Timeout',
                'load_time': 30.0,
                'is_allowed': False
            }
        except requests.exceptions.RequestException as e:
            return {
                'bot_name': bot_name,
                'user_agent_name': user_agent_name,
                'user_agent': user_agent,
                'status': 'NA',
                'reason': f'Erreur réseau: {str(e)[:50]}',
                'status_code': 0,
                'robots_allowed': self.check_robots_permission(robots_parser, user_agent, url),
                'robots_meta': 'Erreur',
                'has_noindex': False,
                'title': 'Erreur',
                'load_time': 0,
                'is_allowed': False
            }

    def check_robots_txt(self, url: str, selected_bots: List[str]) -> Dict:
        """Vérification complète avec la nouvelle logique"""
        try:
            # Récupérer le parser robots.txt
            robots_parser, robots_url = self.get_robots_parser(url)
            
            results = {}
            all_tests = []
            
            for bot in selected_bots:
                if bot not in self.known_bots:
                    continue
                
                bot_info = self.known_bots[bot]
                user_agents = bot_info.get('user_agents', {})
                
                bot_tests = []
                
                # Tester chaque user agent du bot
                for ua_name, user_agent in user_agents.items():
                    test_result = self.test_bot_access(url, bot, ua_name, user_agent, robots_parser)
                    bot_tests.append(test_result)
                    all_tests.append(test_result)
                
                # Déterminer le statut global du bot
                if bot_tests:
                    ok_count = sum(1 for test in bot_tests if test['status'] == 'OK')
                    ko_count = sum(1 for test in bot_tests if test['status'] == 'KO')
                    na_count = sum(1 for test in bot_tests if test['status'] == 'NA')
                    
                    if ok_count > 0:
                        # Au moins un UA fonctionne
                        if ko_count == 0 and na_count == 0:
                            bot_status = 'OK'
                            bot_reason = 'Tous les UA autorisés'
                        else:
                            bot_status = 'OK'
                            bot_reason = f'{ok_count}/{len(bot_tests)} UA autorisés'
                    elif na_count == len(bot_tests):
                        # Tous les tests impossibles
                        bot_status = 'NA'
                        bot_reason = 'Tous les tests impossibles'
                    else:
                        # Tous bloqués ou mix de KO/NA
                        bot_status = 'KO'
                        if ko_count == len(bot_tests):
                            bot_reason = 'Tous les UA bloqués'
                        else:
                            bot_reason = f'{ko_count} bloqués, {na_count} impossibles'
                    
                    results[bot] = {
                        'status': bot_status,
                        'reason': bot_reason,
                        'tests': bot_tests,
                        'summary': {
                            'total': len(bot_tests),
                            'ok': ok_count,
                            'ko': ko_count,
                            'na': na_count
                        }
                    }
            
            return {
                'url': robots_url if robots_url else url,
                'original_url': url,
                'status': 'success',
                'robots_available': robots_parser is not None,
                'results': results,
                'all_tests': all_tests,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'url': url,
                'original_url': url,
                'error': f'Erreur lors de la vérification: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

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
