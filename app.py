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
                    bot_data[bot] = {'Sites autorisant': 0, 'Sites bloquant': 0}
                
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
                    bot_data[bot]['Sites bloquant'] += 1
                else:
                    bot_data[bot]['Sites autorisant'] += 1
    
    if bot_data:
        df_bots = pd.DataFrame(bot_data).T.reset_index()
        df_bots.columns = ['Bot', 'Sites autorisant', 'Sites bloquant']
        return df_bots
    return None

def create_blocking_reasons_chart(results):
    """Analyse des raisons de blocage - retourne les données pour affichage vertical"""
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
                if rules.get('disallowed'):
                    # Vérifier si il y a des règles de blocage importantes
                    important_blocks = [rule for rule in rules['disallowed'] 
                                      if rule in ['/', '/admin', '/private', '/wp-admin', '/api']]
                    if important_blocks:
                        has_disallow_rules = True
                        break
            
            if has_disallow_rules:
                blocking_reasons['Robots.txt Disallow'] += 1
    
    # Filtrer les raisons avec des valeurs > 0
    filtered_reasons = {k: v for k, v in blocking_reasons.items() if v > 0}
    
    if filtered_reasons:
        df_blocking = pd.DataFrame(list(filtered_reasons.items()), columns=['Raison', 'Nombre'])
        return df_blocking
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
        
        # Zone de texte avec clé unique pour éviter les conflits
        urls_text = st.text_area(
            "Une URL par ligne:",
            placeholder="https://example.com\nhttps://monsite.fr\nwww.autresite.com",
            height=150,
            help="Vous pouvez entrer les URLs avec ou sans https://",
            key="url_input_textarea"
        )
        
        # Traitement immédiat du texte saisi
        if urls_text and urls_text.strip():
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            
            # Affichage en temps réel des URLs détectées
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

def create_detailed_results_table(results, selected_bots):
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

def render_results(results, selected_bots):
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
        blocking_df = create_blocking_reasons_chart(results)
        if blocking_df is not None:
            # Graphique horizontal avec couleurs pour les blocages
            st.bar_chart(
                blocking_df.set_index('Raison'),
                horizontal=True,
                color='#ff6b6b'  # Rouge pour les blocages
            )
        else:
            st.info("Aucun blocage détecté")
    
    with col_chart2:
        st.subheader("🤖 Sites par crawler")
        bots_df = create_bots_analysis_data(results)
        if bots_df is not None:
            # Créer le graphique avec des couleurs spécifiques
            chart_data = bots_df.set_index('Bot')[['Sites autorisant', 'Sites bloquant']]
            
            # Utiliser st.bar_chart avec couleurs personnalisées
            st.bar_chart(
                chart_data, 
                horizontal=True,
                color=['#28a745', '#dc3545']  # Vert pour autorisant, Rouge pour bloquant
            )
    
    # Tableau détaillé des résultats
    st.markdown("---")
    st.subheader("📋 Résultats détaillés")
    
    detailed_table = create_detailed_results_table(results, selected_bots)
    
    # Fonction pour colorer les cellules
    def highlight_status(val):
        if isinstance(val, str):
            if val.startswith("OK"):
                return 'background-color: #d4edda; color: #155724'  # Vert
            elif val.startswith("KO"):
                return 'background-color: #f8d7da; color: #721c24'  # Rouge
            elif val.startswith("NA"):
                return 'background-color: #fff3cd; color: #856404'  # Jaune
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

def main():
    # Initialisation des variables de session
    if 'current_urls' not in st.session_state:
        st.session_state.current_urls = []
    
    # Sidebar
    selected_bots = render_sidebar()
    
    # Interface principale
    urls = render_url_input()
    
    # Mise à jour des URLs dans la session
    if urls:
        st.session_state.current_urls = urls
    
    # Section de lancement de l'analyse
    st.markdown("---")
    
    # Utiliser les URLs de la session pour la validation
    current_urls = st.session_state.current_urls if st.session_state.current_urls else urls
    
    # Bouton de vérification avec validation - Correction de la logique
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
        # Forcer la réactivation du bouton en utilisant une clé unique
        button_key = f"launch_analysis_{len(current_urls)}_{len(selected_bots)}_{hash(str(current_urls))}"
        
        if st.button(
            "🚀 Lancer l'analyse", 
            type="primary", 
            disabled=launch_disabled,
            use_container_width=True,
            key=button_key
        ):
            # Vérification finale avant l'analyse
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
                    
                    # Petite pause pour l'UX
                    time.sleep(0.1)
                
                status_text.success("✅ **Analyse terminée avec succès!**")
                
                # Stocker les résultats
                st.session_state.results = results
                st.session_state.selected_bots = selected_bots
                st.session_state.analysis_timestamp = datetime.now()
                
                # Force rerun pour afficher les résultats
                st.rerun()
    
    # Affichage des résultats
    if hasattr(st.session_state, 'results') and st.session_state.results:
        render_results(st.session_state.results, st.session_state.selected_bots)
        
        # Section Export
        st.markdown("---")
        st.markdown("## 💾 Exporter les résultats")
        
        # Centrer le bouton sur la page
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