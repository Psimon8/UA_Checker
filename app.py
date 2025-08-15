import streamlit as st
import pandas as pd
from bots_checker import BotsChecker
from datetime import datetime
import base64
from io import BytesIO

def get_download_link(df, filename):
    """Génère un lien de téléchargement pour le fichier Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Télécharger les résultats Excel</a>'
    return href

def main():
    st.set_page_config(
        page_title="AI Crawlers & Robots.txt Checker",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Crawlers & Robots.txt Checker")
    st.markdown("Vérifiez les règles robots.txt pour différents crawlers IA")
    
    # Initialiser le checker
    checker = BotsChecker()
    
    # Sidebar pour la configuration
    st.sidebar.header("Configuration")
    
    # Sélection des bots
    st.sidebar.subheader("Sélectionner les crawlers IA à tester")
    available_bots = checker.get_bot_list()
    
    # Checkboxes pour chaque bot
    selected_bots = []
    
    # Organiser en colonnes dans la sidebar
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.checkbox("GoogleBot", value=True):
            selected_bots.append("googlebot")
        if st.checkbox("OpenAI (GPTBot)", value=True):
            selected_bots.append("openai")
        if st.checkbox("Perplexity", value=True):
            selected_bots.append("perplexity")
        if st.checkbox("YandexBot"):
            selected_bots.append("yandexbot")
    
    with col2:
        if st.checkbox("BingBot"):
            selected_bots.append("bingbot")
        if st.checkbox("Anthropic (Claude)", value=True):
            selected_bots.append("anthropic")
        if st.checkbox("Cohere"):
            selected_bots.append("cohere")
    
    # Zone principale
    st.header("URLs à tester")
    
    # Options pour saisir les URLs
    input_method = st.radio(
        "Méthode de saisie:",
        ["Texte libre", "Upload fichier", "URLs prédéfinies"]
    )
    
    urls = []
    
    if input_method == "Texte libre":
        urls_text = st.text_area(
            "Entrez les URLs (une par ligne):",
            placeholder="https://example.com\nhttps://another-site.com\nwww.site-without-https.com",
            height=150
        )
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    elif input_method == "Upload fichier":
        uploaded_file = st.file_uploader(
            "Choisir un fichier CSV/TXT avec les URLs",
            type=['csv', 'txt']
        )
        if uploaded_file:
            content = uploaded_file.read().decode()
            urls = [url.strip() for url in content.split('\n') if url.strip()]
    
    elif input_method == "URLs prédéfinies":
        predefined = st.multiselect(
            "Sélectionner des sites populaires:",
            [
                "https://www.yuriandneil.com/",
                "https://www.primelis.com/",
                "https://www.eskimoz.fr/"
            ]
        )
        urls = predefined
    
    # Afficher les URLs sélectionnées
    if urls:
        st.subheader(f"URLs sélectionnées ({len(urls)})")
        for i, url in enumerate(urls[:5], 1):
            st.write(f"{i}. {url}")
        if len(urls) > 5:
            st.write(f"... et {len(urls) - 5} autres")
    
    # Bouton de vérification
    if st.button("🔍 Vérifier les robots.txt", type="primary"):
        if not urls:
            st.error("Veuillez saisir au moins une URL")
        elif not selected_bots:
            st.error("Veuillez sélectionner au moins un crawler")
        else:
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            
            for i, url in enumerate(urls):
                status_text.text(f"Vérification de {url}...")
                progress_bar.progress((i + 1) / len(urls))
                
                result = checker.check_robots_txt(url, selected_bots)
                result['original_url'] = url
                results.append(result)
            
            status_text.text("Vérification terminée!")
            
            # Stocker les résultats dans la session
            st.session_state.results = results
            st.session_state.selected_bots = selected_bots
    
    # Affichage des résultats
    if hasattr(st.session_state, 'results') and st.session_state.results:
        st.header("📊 Résultats")
        
        # Résumé
        total_urls = len(st.session_state.results)
        success_count = sum(1 for r in st.session_state.results if 'error' not in r)
        error_count = total_urls - success_count
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total URLs", total_urls)
        col2.metric("Succès", success_count)
        col3.metric("Erreurs", error_count)
        
        # Détails par URL
        for result in st.session_state.results:
            with st.expander(f"🌐 {result['original_url']}"):
                if 'error' in result:
                    st.error(f"❌ Erreur: {result['error']}")
                else:
                    st.success("✅ Robots.txt trouvé et analysé")
                    
                    # Créer un DataFrame pour l'affichage
                    data = []
                    for bot, rules in result['results'].items():
                        data.append({
                            'Crawler': bot.title(),
                            'Règles Disallow': len(rules.get('disallowed', [])),
                            'Règles Allow': len(rules.get('allowed', [])),
                            'Crawl Delay': rules.get('crawl_delay', 'Non spécifié'),
                            'Détails Disallow': '; '.join(rules.get('disallowed', [])[:3]) + ('...' if len(rules.get('disallowed', [])) > 3 else ''),
                            'Détails Allow': '; '.join(rules.get('allowed', [])[:3]) + ('...' if len(rules.get('allowed', [])) > 3 else '')
                        })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
        
        # Export Excel
        st.header("📥 Export des résultats")
        if st.button("Générer fichier Excel"):
            # Préparer les données pour Excel
            excel_data = []
            for result in st.session_state.results:
                if 'error' in result:
                    excel_data.append({
                        'URL': result['original_url'],
                        'Status': 'Error',
                        'Error': result['error'],
                        'Bot': '',
                        'Allowed_Rules': '',
                        'Disallowed_Rules': '',
                        'Crawl_Delay': '',
                        'Timestamp': result.get('timestamp', '')
                    })
                else:
                    for bot, rules in result['results'].items():
                        excel_data.append({
                            'URL': result['original_url'],
                            'Status': 'Success',
                            'Error': '',
                            'Bot': bot,
                            'Allowed_Rules': '; '.join(rules.get('allowed', [])),
                            'Disallowed_Rules': '; '.join(rules.get('disallowed', [])),
                            'Crawl_Delay': rules.get('crawl_delay', ''),
                            'Timestamp': result.get('timestamp', '')
                        })
            
            df_export = pd.DataFrame(excel_data)
            filename = f"robots_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            st.markdown(get_download_link(df_export, filename), unsafe_allow_html=True)
            st.success("Fichier Excel généré! Cliquez sur le lien ci-dessus pour télécharger.")

if __name__ == "__main__":
    main()
            st.markdown(get_download_link(df_export, filename), unsafe_allow_html=True)
            st.success("Fichier Excel généré! Cliquez sur le lien ci-dessus pour télécharger.")

if __name__ == "__main__":
    main()
