"""
Application principale Streamlit
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime

from bots_checker import BotsChecker
from ui.components import UIComponents
from ui.results_display import ResultsDisplay


# Configuration de la page
st.set_page_config(
    page_title="AI Crawlers & Robots.txt Checker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Fonction principale de l'application"""
    # Initialisation des composants
    ui_components = UIComponents()
    results_display = ResultsDisplay()
    
    # Appliquer les styles
    ui_components.render_css()
    
    # Initialisation des variables de session
    if 'current_urls' not in st.session_state:
        st.session_state.current_urls = []
    
    # Sidebar
    selected_bots = ui_components.render_sidebar()
    
    # En-tête principal
    ui_components.render_header()
    
    # Interface principale
    urls = ui_components.render_url_input()
    
    # Mise à jour des URLs dans la session
    if urls:
        st.session_state.current_urls = urls
    
    # Section de lancement de l'analyse
    st.markdown("---")
    
    # Utiliser les URLs de la session pour la validation
    current_urls = st.session_state.current_urls if st.session_state.current_urls else urls
    
    # Bouton de vérification avec validation
    launch_disabled = False
    
    if len(current_urls) == 0:
        st.warning("⚠️ Veuillez saisir au moins une URL à analyser")
        launch_disabled = True
    elif len(selected_bots) == 0:
        st.warning("⚠️ Veuillez sélectionner au moins un crawler à tester")
        launch_disabled = True
    else:
        st.info(f"🎯 Prêt à analyser **{len(current_urls)} URLs** avec **{len(selected_bots)} crawlers**")
    
    # Bouton de lancement
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    
    with col_btn2:
        button_key = f"launch_analysis_{len(current_urls)}_{len(selected_bots)}_{hash(str(current_urls))}"
        
        if st.button(
            "🚀 Lancer l'analyse", 
            type="primary", 
            disabled=launch_disabled,
            use_container_width=True,
            key=button_key
        ):
            if len(current_urls) > 0 and len(selected_bots) > 0:
                # Barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                
                for i, url in enumerate(current_urls):
                    status_text.info(f"🔍 Analyse en cours: **{url}** ({i+1}/{len(current_urls)})")
                    
                    # Analyse avec le checker
                    checker = BotsChecker()
                    result = checker.check_robots_txt(url, selected_bots)
                    result['original_url'] = url
                    results.append(result)
                    
                    # Update progress
                    progress = (i + 1) / len(current_urls)
                    progress_bar.progress(progress)
                    
                    time.sleep(0.1)
                
                status_text.success("✅ **Analyse terminée avec succès!**")
                
                # Stocker les résultats
                st.session_state.results = results
                st.session_state.selected_bots = selected_bots
                st.session_state.analysis_timestamp = datetime.now()
                
                st.rerun()
    
    # Affichage des résultats
    if hasattr(st.session_state, 'results') and st.session_state.results:
        results_display.render_results(st.session_state.results, st.session_state.selected_bots)
        
        # Section Export
        st.markdown("---")
        st.markdown("## 💾 Exporter les résultats")
        
        col_center1, col_center2, col_center3 = st.columns([2, 1, 2])
        
        with col_center2:
            if st.button("📊 Générer rapport Excel", type="secondary", use_container_width=True):
                # Préparer les données pour Excel
                excel_data = []
                for result in st.session_state.results:
                    if 'error' in result:
                        excel_data.append({
                            'URL': result['original_url'],
                            'Status': 'Error',
                            'Error': result['error'],
                            'Bot': '', 'Test_Details': '',
                            'Timestamp': result.get('timestamp', '')
                        })
                    else:
                        for bot, bot_result in result['results'].items():
                            for test in bot_result.get('tests', []):
                                excel_data.append({
                                    'URL': result['original_url'],
                                    'Status': 'Success',
                                    'Error': '',
                                    'Bot': f"{bot}_{test['user_agent_name']}",
                                    'Test_Details': f"Status: {test['status']}, Reason: {test['reason']}",
                                    'Timestamp': result.get('timestamp', '')
                                })
                
                df_export = pd.DataFrame(excel_data)
                timestamp = st.session_state.analysis_timestamp.strftime('%Y%m%d_%H%M%S')
                filename = f"robots_analysis_{timestamp}.xlsx"
                
                st.markdown(ui_components.get_download_link(df_export, filename), unsafe_allow_html=True)
                st.success("📄 Rapport Excel généré!")
    
    # Footer
    st.markdown("---")
    st.markdown("*🤖 AI Crawlers & Robots.txt Checker - Analysez les permissions des crawlers IA*")


if __name__ == "__main__":
    main()