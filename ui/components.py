"""
Composants UI réutilisables pour l'interface Streamlit
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO

from core.bot_definitions import BOT_MAPPING


class UIComponents:
    """Composants d'interface utilisateur"""
    
    @staticmethod
    def render_css():
        """Applique les styles CSS personnalisés"""
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                color: white;
            }
            .metric-card {
                background: white;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header():
        """Rendu de l'en-tête principal"""
        st.markdown(
            '<div class="main-header">'
            '<h1>🤖 AI Crawlers & Robots.txt Checker</h1>'
            '<p>Analysez les permissions robots.txt pour les crawlers IA sur vos sites web</p>'
            '</div>', 
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_sidebar():
        """Interface sidebar améliorée"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Configuration")
        st.sidebar.markdown("### 🤖 Crawlers IA")
        
        # Groupe moteurs de recherche
        with st.sidebar.expander("🔍 Moteurs de recherche", expanded=True):
            google = st.checkbox("GoogleBot", value=True, key="google")
            bing = st.checkbox("BingBot", value=False, key="bing")
            yandex = st.checkbox("YandexBot", value=False, key="yandex")
        
        # Groupe IA
        with st.sidebar.expander("🧠 Crawlers IA", expanded=True):
            openai = st.checkbox("OpenAI (GPTBot)", value=True, key="openai")
            anthropic = st.checkbox("Anthropic (Claude)", value=True, key="anthropic")
            perplexity = st.checkbox("Perplexity", value=True, key="perplexity")
            cohere = st.checkbox("Cohere", value=False, key="cohere")
        
        # Groupe social
        with st.sidebar.expander("📱 Réseaux sociaux", expanded=False):
            facebook = st.checkbox("Facebook Bot", value=False, key="facebook")
            twitter = st.checkbox("Twitter Bot", value=False, key="twitter")
            linkedin = st.checkbox("LinkedIn Bot", value=False, key="linkedin")
        
        # Construction de la liste des bots sélectionnés
        selected_bots = []
        for key, bot_name in BOT_MAPPING.items():
            if st.session_state.get(key, False):
                selected_bots.append(bot_name)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{len(selected_bots)}** crawlers sélectionnés")
        
        return selected_bots
    
    @staticmethod
    def render_url_input():
        """Interface d'entrée des URLs"""
        # Tabs pour les différentes méthodes d'entrée
        tab1, tab2, tab3 = st.tabs(["📝 Saisie manuelle", "📁 Import fichier", "🌟 Sites prédéfinis"])
        
        urls = []
        
        with tab1:
            st.subheader("Entrez vos URLs")
            urls_text = st.text_area(
                "Une URL par ligne:",
                placeholder="https://example.com\nhttps://monsite.fr\nwww.autresite.com",
                height=150,
                help="Vous pouvez entrer les URLs avec ou sans https://",
                key="url_input_textarea"
            )
            
            if urls_text and urls_text.strip():
                urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
                if urls:
                    st.success(f"✅ {len(urls)} URL(s) détectée(s)")
        
        with tab2:
            st.subheader("Importer depuis un fichier")
            uploaded_file = st.file_uploader(
                "Choisir un fichier (CSV ou TXT)",
                type=['csv', 'txt'],
                help="Le fichier doit contenir une URL par ligne",
                key="file_uploader"
            )
            if uploaded_file:
                try:
                    content = uploaded_file.read().decode('utf-8')
                    file_urls = [url.strip() for url in content.split('\n') if url.strip()]
                    if file_urls:
                        urls = file_urls
                        st.success(f"✅ {len(urls)} URLs importées depuis le fichier")
                    else:
                        st.warning("⚠️ Aucune URL valide trouvée dans le fichier")
                except Exception as e:
                    st.error(f"Erreur lors de la lecture du fichier: {e}")
        
        with tab3:
            st.subheader("Sites d'exemple")
            predefined = st.multiselect(
                "Sélectionner des sites pour les tests:",
                [
                    "https://www.yuriandneil.com/",
                    "https://www.primelis.com/",
                    "https://www.eskimoz.fr/"
                ],
                help="Sites SEO français pour tester les crawlers IA",
                key="predefined_sites"
            )
            if predefined:
                urls = predefined
        
        return urls
    
    @staticmethod
    def get_download_link(df, filename):
        """Génère un lien de téléchargement pour le fichier Excel"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
        
        excel_data = output.getvalue()
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Télécharger Excel</a>'
        return href
