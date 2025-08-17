"""
Module d'affichage des résultats
"""

import streamlit as st
import pandas as pd

from .charts import ChartCreator


class ResultsDisplay:
    """Gestionnaire d'affichage des résultats"""
    
    def __init__(self):
        self.chart_creator = ChartCreator()
    
    def create_detailed_results_table(self, results, selected_bots):
        """Crée un tableau détaillé avec le statut OK/KO/NA pour chaque site et crawler"""
        table_data = []
        
        for result in results:
            row = {'Site': result['original_url']}
            
            if 'error' in result:
                # Si erreur globale, tous les bots sont NA
                for bot in selected_bots:
                    row[bot.upper()] = f"NA (Erreur: {result['error'][:30]}...)"
            else:
                # Analyser chaque bot avec les nouveaux résultats
                for bot in selected_bots:
                    if bot in result.get('results', {}):
                        bot_result = result['results'][bot]
                        status = bot_result.get('status', 'NA')
                        reason = bot_result.get('reason', 'Raison inconnue')
                        summary = bot_result.get('summary', {})
                        
                        # Format amélioré avec détails
                        if status == 'OK':
                            if summary.get('total', 0) > 1:
                                ok_count = summary.get('ok', 0)
                                total = summary.get('total', 1)
                                if ok_count == total:
                                    row[bot.upper()] = "OK (Tous UA)"
                                else:
                                    row[bot.upper()] = f"OK ({ok_count}/{total} UA)"
                            else:
                                row[bot.upper()] = "OK"
                        elif status == 'KO':
                            if 'Tous les UA bloqués' in reason:
                                row[bot.upper()] = "KO (Tous bloqués)"
                            elif 'robots.txt' in reason.lower():
                                row[bot.upper()] = "KO (Robots.txt)"
                            elif 'http' in reason.lower():
                                row[bot.upper()] = "KO (HTTP)"
                            elif 'noindex' in reason.lower():
                                row[bot.upper()] = "KO (Meta noindex)"
                            else:
                                row[bot.upper()] = f"KO ({reason[:15]}...)"
                        else:  # NA
                            if 'timeout' in reason.lower():
                                row[bot.upper()] = "NA (Timeout)"
                            elif 'impossible' in reason.lower():
                                row[bot.upper()] = "NA (Test impossible)"
                            elif 'erreur' in reason.lower():
                                row[bot.upper()] = "NA (Erreur réseau)"
                            else:
                                row[bot.upper()] = f"NA ({reason[:15]}...)"
                    else:
                        row[bot.upper()] = "NA (Non testé)"
            
            table_data.append(row)
        
        return pd.DataFrame(table_data)
    
    def render_results(self, results, selected_bots):
        """Affichage amélioré des résultats"""
        st.markdown("## 📊 Résultats de l'analyse")
        
        # Métriques globales améliorées
        total_urls = len(results)
        success_count = sum(1 for r in results if 'error' not in r)
        error_count = total_urls - success_count
        
        # Calcul des statistiques par statut
        ok_count = 0
        ko_count = 0
        na_count = 0
        total_tests = 0
        
        for result in results:
            if 'error' not in result and 'all_tests' in result:
                for test in result['all_tests']:
                    total_tests += 1
                    status = test.get('status', 'NA')
                    if status == 'OK':
                        ok_count += 1
                    elif status == 'KO':
                        ko_count += 1
                    else:
                        na_count += 1
        
        # Affichage des métriques
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🔍 URLs analysées", total_urls)
        
        with col2:
            st.metric("✅ Tests OK", ok_count)
        
        with col3:
            st.metric("❌ Tests KO", ko_count)
        
        with col4:
            st.metric("⚠️ Tests NA", na_count)
        
        with col5:
            success_rate = (ok_count / total_tests * 100) if total_tests > 0 else 0
            st.metric("📈 Taux de succès", f"{success_rate:.1f}%")

        # Graphiques avec Streamlit natif
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("🚫 Raisons de blocage")
            blocking_df = self.chart_creator.create_blocking_reasons_chart(results)
            if blocking_df is not None:
                st.bar_chart(
                    blocking_df.set_index('Raison'),
                    horizontal=True,
                    color='#ff6b6b'
                )
            else:
                st.info("Aucun blocage détecté")
        
        with col_chart2:
            st.subheader("🤖 Sites par crawler")
            bots_df = self.chart_creator.create_bots_analysis_data(results)
            if bots_df is not None:
                chart_data = bots_df.set_index('Bot')[['Sites autorisant', 'Sites bloquant']]
                st.bar_chart(
                    chart_data, 
                    horizontal=True,
                    color=['#28a745', '#dc3545']
                )
        
        # Tableau détaillé des résultats
        st.markdown("---")
        st.subheader("📋 Résultats détaillés")
        
        detailed_table = self.create_detailed_results_table(results, selected_bots)
        
        # Fonction pour colorer les cellules
        def highlight_status(val):
            if isinstance(val, str):
                if val.startswith("OK"):
                    return 'background-color: #d4edda; color: #155724'
                elif val.startswith("KO"):
                    return 'background-color: #f8d7da; color: #721c24'
                elif val.startswith("NA"):
                    return 'background-color: #fff3cd; color: #856404'
            return ''
        
        # Appliquer le style et afficher le tableau complet
        styled_table = detailed_table.style.applymap(highlight_status)
        st.dataframe(styled_table, use_container_width=True, height=400)
        
        # Légende mise à jour
        st.markdown("""
        **Légende (nouvelle logique):**
        - 🟢 **OK** : Status 200 + Robots.txt autorise + Pas de meta noindex
        - 🔴 **KO** : Status ≠ 200 OU Robots.txt bloque OU Meta noindex présent
        - 🟡 **NA** : Test impossible (timeout, erreur réseau)
        
        **Note :** Un bot est OK si au moins un de ses User-Agents est autorisé.
        """)
