"""
Modules pour la création des graphiques et visualisations
"""

import pandas as pd


class ChartCreator:
    """Créateur de graphiques pour l'interface"""
    
    @staticmethod
    def create_blocking_reasons_chart(results):
        """Analyse des raisons de blocage"""
        blocking_reasons = {
            'Code 403 (Forbidden)': 0,
            'Code 404 (Not Found)': 0,
            'Code 500 (Server Error)': 0,
            'Robots.txt Disallow': 0,
            'No robots.txt': 0,
            'Connection Error': 0
        }
        
        for result in results:
            if 'error' in result:
                if '403' in result['error']:
                    blocking_reasons['Code 403 (Forbidden)'] += 1
                elif '404' in result['error']:
                    blocking_reasons['Code 404 (Not Found)'] += 1
                elif '500' in result['error']:
                    blocking_reasons['Code 500 (Server Error)'] += 1
                elif 'robots.txt' in result['error'].lower():
                    blocking_reasons['No robots.txt'] += 1
                else:
                    blocking_reasons['Connection Error'] += 1
            else:
                # Analyser les règles de blocage dans robots.txt
                has_disallow_rules = False
                for bot, rules in result.get('results', {}).items():
                    if hasattr(rules, 'get') and rules.get('tests'):
                        for test in rules['tests']:
                            if not test.get('robots_allowed', True):
                                has_disallow_rules = True
                                break
                    if has_disallow_rules:
                        break
                
                if has_disallow_rules:
                    blocking_reasons['Robots.txt Disallow'] += 1
        
        # Filtrer les raisons avec des valeurs > 0
        filtered_reasons = {k: v for k, v in blocking_reasons.items() if v > 0}
        
        if filtered_reasons:
            df_blocking = pd.DataFrame(list(filtered_reasons.items()), columns=['Raison', 'Nombre'])
            return df_blocking
        return None
    
    @staticmethod
    def create_bots_analysis_data(results):
        """Analyse des sites autorisant/bloquant par bot"""
        bot_data = {}
        
        for result in results:
            if 'error' not in result and 'results' in result:
                for bot, bot_result in result['results'].items():
                    if bot not in bot_data:
                        bot_data[bot] = {'Sites autorisant': 0, 'Sites bloquant': 0}
                    
                    # Utiliser le statut du bot pour déterminer l'autorisation
                    status = bot_result.get('status', 'NA')
                    if status == 'OK':
                        bot_data[bot]['Sites autorisant'] += 1
                    elif status == 'KO':
                        bot_data[bot]['Sites bloquant'] += 1
                    # Les statuts 'NA' ne sont comptés ni comme autorisant ni comme bloquant
        
        if bot_data:
            df_bots = pd.DataFrame(bot_data).T.reset_index()
            df_bots.columns = ['Bot', 'Sites autorisant', 'Sites bloquant']
            return df_bots
        return None
