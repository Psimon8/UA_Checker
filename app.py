import streamlit as st
import pandas as pd
from bots_checker import BotsChecker
from datetime import datetime
import base64
from io import BytesIO
import time

# Configuration de la page
st.set_page_config(
    page_title="AI Crawlers & Robots.txt Checker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
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

def get_download_link(df, filename):
    """Génère un lien de téléchargement pour le fichier Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Télécharger Excel</a>'
    return href

def create_status_chart(results):
    """Crée un graphique des statuts avec Streamlit natif"""
    status_counts = {'Success': 0, 'Error': 0}
    
    for result in results:
        if 'error' in result:
            status_counts['Error'] += 1
        else:
            status_counts['Success'] += 1
    
    df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
    return df_status

def create_bots_analysis_data(results):
    """Analyse des sites autorisant/bloquant par bot - retourne les données pour affichage horizontal"""
    bot_data = {}
    
    for result in results:
        if 'error' not in result:
            for bot, rules in result['results'].items():
                if bot not in bot_data:
                    bot_data[bot] = {'sites_autorisant': 0, 'sites_bloquant': 0}
                
                # Un site bloque si il y a des règles disallow importantes
                has_blocking_rules = any(
                    rule in ['/', '/admin', '/private', '/wp-admin'] 
                    for rule in rules.get('disallowed', [])
                )
                
                # Un site autorise si pas de règles bloquantes majeures ou règles allow explicites
                has_allowing_rules = (
                    not has_blocking_rules or 
                    len(rules.get('allowed', [])) > 0
                )
                
                if has_blocking_rules:
                    bot_data[bot]['sites_bloquant'] += 1
                else:
                    bot_data[bot]['sites_autorisant'] += 1
    
    if bot_data:
        df_bots = pd.DataFrame(bot_data).T.reset_index()
        df_bots.columns = ['Bot', 'Sites autorisant', 'Sites bloquant']
        return df_bots
    return None

def render_sidebar():
    """Interface sidebar améliorée"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuration")
    
    # Sélection des bots avec groupes
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
    bot_mapping = {
        'google': 'googlebot', 'bing': 'bingbot', 'yandex': 'yandexbot',
        'openai': 'openai', 'anthropic': 'anthropic', 'perplexity': 'perplexity',
        'cohere': 'cohere', 'facebook': 'facebookbot', 'twitter': 'twitterbot',
        'linkedin': 'linkedinbot'
    }
    
    for key, bot_name in bot_mapping.items():
        if st.session_state.get(key, False):
            selected_bots.append(bot_name)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{len(selected_bots)}** crawlers sélectionnés")
    
    return selected_bots

def render_url_input():
    """Interface d'entrée des URLs améliorée"""
    st.markdown('<div class="main-header"><h1>🤖 AI Crawlers & Robots.txt Checker</h1><p>Analysez les permissions robots.txt pour les crawlers IA sur vos sites web</p></div>', unsafe_allow_html=True)
    
    # Tabs pour les différentes méthodes d'entrée
    tab1, tab2, tab3 = st.tabs(["📝 Saisie manuelle", "📁 Import fichier", "🌟 Sites prédéfinis"])
    
    urls = []
    
    with tab1:
        st.subheader("Entrez vos URLs")
        urls_text = st.text_area(
            "Une URL par ligne:",
            placeholder="https://example.com\nhttps://monsite.fr\nwww.autresite.com",
            height=150,
            help="Vous pouvez entrer les URLs avec ou sans https://"
        )
        if urls_text:
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    with tab2:
        st.subheader("Importer depuis un fichier")
        uploaded_file = st.file_uploader(
            "Choisir un fichier (CSV ou TXT)",
            type=['csv', 'txt'],
            help="Le fichier doit contenir une URL par ligne"
        )
        if uploaded_file:
            try:
                content = uploaded_file.read().decode('utf-8')
                urls = [url.strip() for url in content.split('\n') if url.strip()]
                st.success(f"✅ {len(urls)} URLs importées")
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
            help="Sites SEO français pour tester les crawlers IA"
        )
        urls = predefined
    
    # Affichage des URLs sélectionnées
    if urls:
        st.markdown("### 📋 URLs à analyser")
        
        # Affichage en colonnes
        cols = st.columns(min(len(urls), 3))
        for i, url in enumerate(urls):
            with cols[i % 3]:
                st.markdown(f"**{i+1}.** `{url}`")
        
        if len(urls) > 9:
            st.info(f"Et {len(urls) - 9} autres URLs...")
    
    return urls

def render_results(results, selected_bots):
    """Affichage amélioré des résultats"""
    st.markdown("## 📊 Résultats de l'analyse")
    
    # Métriques globales
    total_urls = len(results)
    success_count = sum(1 for r in results if 'error' not in r)
    error_count = total_urls - success_count
    
    # Affichage des métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔍 URLs analysées", total_urls)
    
    with col2:
        st.metric("✅ Succès", success_count, delta=f"{success_count/total_urls*100:.1f}%")
    
    with col3:
        st.metric("❌ Erreurs", error_count, delta=f"{error_count/total_urls*100:.1f}%" if error_count > 0 else None)
    
    with col4:
        st.metric("🤖 Bots testés", len(selected_bots))
    
    # Graphiques avec Streamlit natif
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 Statut des analyses")
        status_df = create_status_chart(results)
        st.bar_chart(status_df.set_index('Status'))
    
    with col_chart2:
        st.subheader("🤖 Sites par crawler")
        bots_df = create_bots_analysis_data(results)
        if bots_df is not None:
            # Affichage horizontal avec barres empilées
            st.bar_chart(bots_df.set_index('Bot'), horizontal=True)

def main():
    # Sidebar
    selected_bots = render_sidebar()
    
    # Interface principale
    urls = render_url_input()
    
    # Section de lancement de l'analyse
    st.markdown("---")
    
    # Bouton de vérification avec validation
    if len(urls) == 0:
        st.warning("⚠️ Veuillez sélectionner au moins une URL à analyser")
        launch_disabled = True
    elif len(selected_bots) == 0:
        st.warning("⚠️ Veuillez sélectionner au moins un crawler à tester")
        launch_disabled = True
    else:
        launch_disabled = False
        st.info(f"🎯 Prêt à analyser **{len(urls)} URLs** avec **{len(selected_bots)} crawlers**")
    
    # Bouton de lancement
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    
    with col_btn2:
        if st.button(
            "🚀 Lancer l'analyse", 
            type="primary", 
            disabled=launch_disabled,
            use_container_width=True
        ):
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            
            for i, url in enumerate(urls):
                status_text.info(f"🔍 Analyse en cours: **{url}** ({i+1}/{len(urls)})")
                
                # Analyse avec le checker
                checker = BotsChecker()
                result = checker.check_robots_txt(url, selected_bots)
                result['original_url'] = url
                results.append(result)
                
                # Update progress
                progress = (i + 1) / len(urls)
                progress_bar.progress(progress)
                
                # Petite pause pour l'UX
                time.sleep(0.1)
            
            status_text.success("✅ **Analyse terminée avec succès!**")
            
            # Stocker les résultats
            st.session_state.results = results
            st.session_state.selected_bots = selected_bots
            st.session_state.analysis_timestamp = datetime.now()
    
    # Affichage des résultats
    if hasattr(st.session_state, 'results') and st.session_state.results:
        render_results(st.session_state.results, st.session_state.selected_bots)
        
        # Section Export
        st.markdown("---")
        st.markdown("## 💾 Exporter les résultats")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📊 Générer rapport Excel", type="secondary", use_container_width=True):
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
                timestamp = st.session_state.analysis_timestamp.strftime('%Y%m%d_%H%M%S')
                filename = f"robots_analysis_{timestamp}.xlsx"
                
                st.markdown(get_download_link(df_export, filename), unsafe_allow_html=True)
                st.success("📄 Rapport Excel généré!")
        
        with col_export2:
            # Afficher les stats de l'analyse
            analysis_time = st.session_state.analysis_timestamp.strftime('%d/%m/%Y à %H:%M')
            st.info(f"📅 **Analyse effectuée le:** {analysis_time}")
        
        # Résultats détaillés par URL (déplacé après l'export)
        st.markdown("---")
        st.markdown("### 📋 Détails par URL")
        
        for i, result in enumerate(st.session_state.results):
            with st.expander(f"🌐 {result['original_url']}", expanded=False):
                if 'error' in result:
                    st.error(f"❌ **Erreur:** {result['error']}")
                else:
                    st.success("✅ **Robots.txt analysé avec succès**")
                    
                    # Créer des onglets pour chaque bot
                    if result['results']:
                        bot_tabs = st.tabs([bot.title() for bot in result['results'].keys()])
                        
                        for j, (bot, rules) in enumerate(result['results'].items()):
                            with bot_tabs[j]:
                                col_info1, col_info2, col_info3 = st.columns(3)
                                
                                with col_info1:
                                    st.metric("🚫 Règles Disallow", len(rules.get('disallowed', [])))
                                
                                with col_info2:
                                    st.metric("✅ Règles Allow", len(rules.get('allowed', [])))
                                
                                with col_info3:
                                    crawl_delay = rules.get('crawl_delay', 'Non spécifié')
                                    st.metric("⏱️ Crawl Delay", f"{crawl_delay}s" if crawl_delay != 'Non spécifié' else crawl_delay)
                                
                                # Détails des règles
                                if rules.get('disallowed'):
                                    st.markdown("**🚫 Chemins bloqués:**")
                                    for path in rules['disallowed'][:10]:  # Limiter à 10
                                        st.code(path)
                                    if len(rules['disallowed']) > 10:
                                        st.info(f"... et {len(rules['disallowed']) - 10} autres règles")
                                
                                if rules.get('allowed'):
                                    st.markdown("**✅ Chemins autorisés:**")
                                    for path in rules['allowed'][:10]:  # Limiter à 10
                                        st.code(path)
                                    if len(rules['allowed']) > 10:
                                        st.info(f"... et {len(rules['allowed']) - 10} autres règles")
    
    # Footer
    st.markdown("---")
    st.markdown("*🤖 AI Crawlers & Robots.txt Checker - Analysez les permissions des crawlers IA*")

if __name__ == "__main__":
    main()