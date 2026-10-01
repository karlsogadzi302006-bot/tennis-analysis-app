import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# 1. CONFIGURATION STREAMLIT & THEME CYBER LUXE (DARK MODE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tennis ValueBet AI Pro",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection CSS : Direction Artistique Dark Luxe / Glassmorphism
st.markdown("""
<style>
    /* THÈME GLOBAL DARK LUXE */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* TITRE ET HEADER UNIQUE */
    .main-title {
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
        margin: 0 !important;
    }
    
    .sub-title {
        font-size: 0.95rem !important;
        color: #94a3b8 !important;
        margin-top: 4px !important;
        margin-bottom: 25px !important;
    }

    /* TITRES DE SECTIONS */
    .cat-title-matchup { color: #fb7185; font-size: 1.25rem; font-weight: 800; margin-bottom: 12px; }
    .cat-title-service { color: #38bdf8; font-size: 1.25rem; font-weight: 800; margin-top: 24px; margin-bottom: 12px; }
    .cat-title-h2h { color: #a855f7; font-size: 1.25rem; font-weight: 800; margin-top: 24px; margin-bottom: 12px; }
    .cat-title-valuebet { color: #f59e0b; font-size: 1.25rem; font-weight: 800; margin-top: 24px; margin-bottom: 12px; }
    .cat-title-annexes { color: #10b981; font-size: 1.25rem; font-weight: 800; margin-top: 24px; margin-bottom: 12px; }

    /* CARTES EN-TÊTE JOUEURS */
    .player-card-a {
        border: 1px solid rgba(244, 63, 94, 0.4) !important;
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.08) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
    }

    .player-card-b {
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
    }

    .player-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .player-name-a { color: #fb7185 !important; font-weight: 800 !important; font-size: 1.15rem !important; }
    .player-name-b { color: #34d399 !important; font-weight: 800 !important; font-size: 1.15rem !important; }

    .style-badge-a {
        background-color: rgba(244, 63, 94, 0.15) !important;
        color: #fda4af !important;
        border: 1px solid rgba(244, 63, 94, 0.3) !important;
        border-radius: 6px !important;
        padding: 3px 10px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }

    .style-badge-b {
        background-color: rgba(16, 185, 129, 0.15) !important;
        color: #a7f3d0 !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 6px !important;
        padding: 3px 10px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }

    /* TUILES MÉTRIQUES */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
    }

    /* BOX D'ANALYSE TACTIQUE */
    .analysis-box {
        background-color: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #38bdf8;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 12px;
        margin-bottom: 16px;
        font-size: 0.92rem;
        color: #e2e8f0;
    }

    /* TERMINAL VALUEBET */
    .ev-card-success {
        border: 1.5px solid #10b981 !important;
        background: rgba(16, 185, 129, 0.1) !important;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.2) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin-bottom: 10px !important;
    }

    .ev-card-danger {
        border: 1.5px solid #f43f5e !important;
        background: rgba(244, 63, 94, 0.1) !important;
        box-shadow: 0 0 12px rgba(244, 63, 94, 0.15) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin-bottom: 10px !important;
    }
</style>

<!-- HEADER UNIQUE -->
<div class='main-title'>🎾 Tennis ValueBet AI Pro</div>
<div class='sub-title'>Plateforme d'Analyse Prédictive & Détection +EV • ATP Circuit</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DONNÉES & CONFIGURATIONS
# ---------------------------------------------------------
SURFACE_FACTORS = {
    "Dur rapide": {"serve_weight": 1.25, "return_weight": 0.85, "base_surface": "Hard"},
    "Dur moyen": {"serve_weight": 1.00, "return_weight": 1.00, "base_surface": "Hard"},
    "Dur lent": {"serve_weight": 0.85, "return_weight": 1.15, "base_surface": "Hard"},
    "Terre battue rapide": {"serve_weight": 0.90, "return_weight": 1.10, "base_surface": "Clay"},
    "Terre battue moyenne": {"serve_weight": 0.75, "return_weight": 1.25, "base_surface": "Clay"},
    "Terre battue lente": {"serve_weight": 0.65, "return_weight": 1.35, "base_surface": "Clay"},
    "Gazon rapide": {"serve_weight": 1.40, "return_weight": 0.70, "base_surface": "Grass"},
    "Gazon moyen": {"serve_weight": 1.20, "return_weight": 0.80, "base_surface": "Grass"},
    "Moquette / Indoor": {"serve_weight": 1.30, "return_weight": 0.75, "base_surface": "Hard"}
}

STYLE_SIMILARITY = {
    "Gros Serveur": {"Gros Serveur": 1.0, "Serveur-Volleyeur": 0.9, "Attaquant du fond": 0.6, "Polyvalent": 0.5, "Relanceur / Cadenceur": 0.3, "Contreur / Limeur": 0.2},
    "Serveur-Volleyeur": {"Gros Serveur": 0.9, "Serveur-Volleyeur": 1.0, "Attaquant du fond": 0.6, "Polyvalent": 0.6, "Relanceur / Cadenceur": 0.4, "Contreur / Limeur": 0.3},
    "Attaquant du fond": {"Gros Serveur": 0.6, "Serveur-Volleyeur": 0.6, "Attaquant du fond": 1.0, "Polyvalent": 0.8, "Relanceur / Cadenceur": 0.7, "Contreur / Limeur": 0.6},
    "Polyvalent": {"Gros Serveur": 0.5, "Serveur-Volleyeur": 0.6, "Attaquant du fond": 0.8, "Polyvalent": 1.0, "Relanceur / Cadenceur": 0.8, "Contreur / Limeur": 0.8},
    "Relanceur / Cadenceur": {"Gros Serveur": 0.3, "Serveur-Volleyeur": 0.4, "Attaquant du fond": 0.7, "Polyvalent": 0.8, "Relanceur / Cadenceur": 1.0, "Contreur / Limeur": 0.9},
    "Contreur / Limeur": {"Gros Serveur": 0.2, "Serveur-Volleyeur": 0.3, "Attaquant du fond": 0.6, "Polyvalent": 0.8, "Relanceur / Cadenceur": 0.9, "Contreur / Limeur": 1.0}
}


@st.cache_data
def load_data():
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    df_list = []
    for y in years:
        url = f"https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_{y}.csv"
        try:
            df = pd.read_csv(url)
            if not df.empty and 'winner_name' in df.columns:
                df_list.append(df)
        except Exception:
            pass
            
    if not df_list:
        # DataFrame de secours si le téléchargement échoue
        return pd.DataFrame(columns=['winner_name', 'loser_name', 'winner_clean', 'loser_clean', 'tourney_date', 'surface', 'score'])
    
    df_all = pd.concat(df_list, ignore_index=True)
    
    # Création explicite des colonnes nettoyées
    df_all['winner_clean'] = df_all['winner_name'].astype(str).str.strip().str.lower()
    df_all['loser_clean'] = df_all['loser_name'].astype(str).str.strip().str.lower()
    df_all['tourney_date'] = pd.to_datetime(df_all['tourney_date'].astype(str), format='%Y%m%d', errors='coerce')
    
    def calc_games(score_str):
        if not isinstance(score_str, str): return np.nan
        games = 0
        for set_s in score_str.split():
            parts = set_s.split('-')
            if len(parts) >= 2:
                try:
                    w = int(parts[0].replace('(', '').replace(')', ''))
                    l = int(parts[1].split('(')[0])
                    games += (w + l)
                except ValueError:
                    pass
        return games if games > 0 else np.nan

    df_all['total_games'] = df_all['score'].apply(calc_games)
    return df_all

df_circuit = load_data()

def clean_name(name):
    return str(name).strip().lower()

def get_player_matches(df, player_name):
    clean_p = clean_name(player_name)
    
    # Vérification de sécurité sur la présence des colonnes
    if df.empty or 'winner_clean' not in df.columns or 'loser_clean' not in df.columns:
        return pd.DataFrame(), pd.DataFrame()
        
    p_wins = df[df['winner_clean'] == clean_p].copy()
    p_losses = df[df['loser_clean'] == clean_p].copy()
    
    p_wins = p_wins.drop_duplicates(subset=['tourney_date', 'loser_clean', 'score']) if not p_wins.empty else p_wins
    p_losses = p_losses.drop_duplicates(subset=['tourney_date', 'winner_clean', 'score']) if not p_losses.empty else p_losses
    
    return p_wins, p_losses

player_styles_map = {}
if not df_circuit.empty:
    all_players = set(df_circuit['winner_name'].dropna()).union(set(df_circuit['loser_name'].dropna()))
    for p in all_players:
        pw, pl = get_player_matches(df_circuit, p)
        tot = len(pw) + len(pl)
        if tot < 3:
            player_styles_map[p] = "Polyvalent"
            continue
        
        aces = pd.concat([pw['w_ace'], pl['l_ace']]).dropna()
        svpt = pd.concat([pw['w_svpt'], pl['l_svpt']]).sum()
        fst_won = pd.concat([pw['w_1stwon'], pl['l_1stwon']]).sum()
        
        avg_aces = aces.mean() if len(aces) > 0 else 2.0
        pct_1st_won = (fst_won / svpt * 100) if svpt > 0 else 65.0
        
        if avg_aces >= 8.5 or pct_1st_won >= 78.0:
            player_styles_map[p] = "Gros Serveur"
        elif avg_aces >= 6.0 and pct_1st_won >= 73.0:
            player_styles_map[p] = "Serveur-Volleyeur"
        elif pct_1st_won <= 63.0 and avg_aces <= 2.5:
            player_styles_map[p] = "Contreur / Limeur"
        elif avg_aces <= 3.5:
            player_styles_map[p] = "Relanceur / Cadenceur"
        else:
            player_styles_map[p] = "Attaquant du fond"

# ---------------------------------------------------------
# 3. EXTRACTION SECURISEE DES METRIQUES
# ---------------------------------------------------------
def get_detailed_metrics(player, detailed_surface):
    s_config = SURFACE_FACTORS.get(detailed_surface, {"serve_weight": 1.0, "return_weight": 1.0, "base_surface": "Hard"})
    base_surf = s_config["base_surface"]
    
    p_wins, p_losses = get_player_matches(df_circuit, player)
    total_m = len(p_wins) + len(p_losses)
    player_style = player_styles_map.get(player, "Polyvalent")

    # VALEURS NEUTRES PAR DÉFAUT SI JOUEUR ITF/SANS DATA
    if total_m == 0:
        return {
            "player_name": player, "overall_winrate": 0.40, "recent_form": 0.40,
            "surface_winrate": 0.40, "style": player_style, "total_matches": 0,
            "last_10_wins": 4, "avg_aces": 1.5, "avg_dfs": 2.0,
            "pct_1st_in": 60.0, "pct_1st_won": 65.0, "avg_games": 21.5, "pct_3_sets": 30.0,
            "pct_tb": 20.0, "p_wins": p_wins, "p_losses": p_losses,
            "serve_weight": s_config["serve_weight"], "return_weight": s_config["return_weight"]
        }

    overall_winrate = len(p_wins) / total_m
    all_matches = pd.concat([p_wins.assign(is_win=1), p_losses.assign(is_win=0)]).sort_values(by='tourney_date', ascending=False)
    last_10 = all_matches.head(10)
    recent_form = last_10['is_win'].mean() if len(last_10) > 0 else 0.5
    
    surf_wins = p_wins[p_wins['surface'] == base_surf]
    surf_losses = p_losses[p_losses['surface'] == base_surf]
    surf_matches = pd.concat([surf_wins.assign(is_win=1), surf_losses.assign(is_win=0)]).sort_values(by='tourney_date', ascending=False)
    
    total_surf = len(surf_matches)
    raw_surface_winrate = len(surf_wins) / total_surf if total_surf >= 3 else overall_winrate

    style_speed_factor = 1.0
    if player_style in ["Gros Serveur", "Serveur-Volleyeur"]:
        style_speed_factor = s_config["serve_weight"]
    elif player_style in ["Relanceur / Cadenceur", "Contreur / Limeur"]:
        style_speed_factor = s_config["return_weight"]
        
    adjusted_surface_winrate = min(max(raw_surface_winrate * ((style_speed_factor + 1.0) / 2.0), 0.05), 0.95)
    target_matches = surf_matches.head(12) if total_surf >= 5 else all_matches.head(12)
    
    w_surf = target_matches[target_matches['is_win'] == 1]
    l_surf = target_matches[target_matches['is_win'] == 0]
    
    aces = pd.concat([w_surf['w_ace'], l_surf['l_ace']]).dropna() if ('w_ace' in w_surf.columns and 'l_ace' in l_surf.columns) else pd.Series([2.0])
    dfs_count = pd.concat([w_surf['w_df'], l_surf['l_df']]).dropna() if ('w_df' in w_surf.columns and 'l_df' in l_surf.columns) else pd.Series([2.0])
    
    svpt = pd.concat([w_surf['w_svpt'], l_surf['l_svpt']]).sum() if ('w_svpt' in w_surf.columns and 'l_svpt' in l_surf.columns) else 0
    fst_in = pd.concat([w_surf['w_1stin'], l_surf['l_1stin']]).sum() if ('w_1stin' in w_surf.columns and 'l_1stin' in l_surf.columns) else 0
    fst_won = pd.concat([w_surf['w_1stwon'], l_surf['l_1stwon']]).sum() if ('w_1stwon' in w_surf.columns and 'l_1stwon' in l_surf.columns) else 0
    
    pct_1st_in = (fst_in / svpt * 100) if svpt > 0 else 60.0
    pct_1st_won = (fst_won / fst_in * 100) if fst_in > 0 else 66.0

    return {
        "player_name": player, "overall_winrate": overall_winrate, "recent_form": recent_form,
        "surface_winrate": adjusted_surface_winrate, "style": player_style, "total_matches": total_m,
        "last_10_wins": int(recent_form * len(last_10)),
        "avg_aces": aces.mean() * s_config["serve_weight"] if len(aces) > 0 else 2.0,
        "avg_dfs": dfs_count.mean() if len(dfs_count) > 0 else 2.0,
        "pct_1st_in": pct_1st_in, "pct_1st_won": pct_1st_won,
        "avg_games": 22.0, "pct_3_sets": 30.0, "pct_tb": 20.0,
        "p_wins": p_wins, "p_losses": p_losses,
        "serve_weight": s_config["serve_weight"], "return_weight": s_config["return_weight"]
    }

# ---------------------------------------------------------
# 4. SIDEBAR SELECTION
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configuration du Match")

all_players_list = sorted(list(set(df_circuit['winner_name'].dropna()).union(set(df_circuit['loser_name'].dropna())))) if not df_circuit.empty else ["Player A", "Player B"]

player_a = st.sidebar.selectbox("Joueur A", all_players_list, index=0)
player_b = st.sidebar.selectbox("Joueur B", all_players_list, index=min(1, len(all_players_list)-1))
surface = st.sidebar.selectbox("Surface spécifique", list(SURFACE_FACTORS.keys()), index=0)

stats_a = get_detailed_metrics(player_a, surface)
stats_b = get_detailed_metrics(player_b, surface)

# ---------------------------------------------------------
# 5. ALGORITHME PONDÉRÉ EN 5 PILIERS (35/25/25/15)
# ---------------------------------------------------------
def get_weighted_winrate_vs_style(stats_player, target_style):
    weighted_wins, weighted_total = 0.0, 0.0
    if 'loser_name' in stats_player['p_wins'].columns:
        for opp in stats_player['p_wins']['loser_name']:
            opp_style = player_styles_map.get(opp, "Polyvalent")
            sim_score = STYLE_SIMILARITY.get(target_style, {}).get(opp_style, 0.3)
            weighted_wins += 1.0 * sim_score
            weighted_total += 1.0 * sim_score

    if 'winner_name' in stats_player['p_losses'].columns:
        for opp in stats_player['p_losses']['winner_name']:
            opp_style = player_styles_map.get(opp, "Polyvalent")
            sim_score = STYLE_SIMILARITY.get(target_style, {}).get(opp_style, 0.3)
            weighted_total += 1.0 * sim_score

    return (weighted_wins / weighted_total) if weighted_total >= 1.0 else stats_player['overall_winrate']

# Pilier 1 : Surface (35%)
serve_adj_a = (stats_a['pct_1st_won'] / 100.0) * stats_a['serve_weight']
serve_adj_b = (stats_b['pct_1st_won'] / 100.0) * stats_b['serve_weight']
p1_a = ((stats_a['surface_winrate'] * 80.0) + (serve_adj_a * 20.0)) * 3.5
p1_b = ((stats_b['surface_winrate'] * 80.0) + (serve_adj_b * 20.0)) * 3.5

# Pilier 2 : Forme (25%)
p2_a, p2_b = (stats_a['recent_form'] * 100.0) * 2.5, (stats_b['recent_form'] * 100.0) * 2.5

# Pilier 3 : Matchup (25%)
winrate_a_vs_b_style = get_weighted_winrate_vs_style(stats_a, stats_b['style'])
winrate_b_vs_a_style = get_weighted_winrate_vs_style(stats_b, stats_a['style'])
p3_a, p3_b = (winrate_a_vs_b_style * 100.0) * 2.5, (winrate_b_vs_a_style * 100.0) * 2.5

# Pilier 4 : H2H & Laplace Smoothing (15%)
clean_a, clean_b = clean_name(player_a), clean_name(player_b)
h2h_matches = df_circuit[
    ((df_circuit['winner_clean'] == clean_a) & (df_circuit['loser_clean'] == clean_b)) |
    ((df_circuit['winner_clean'] == clean_b) & (df_circuit['loser_clean'] == clean_a))
].copy() if not df_circuit.empty else pd.DataFrame()

s_config = SURFACE_FACTORS.get(surface, {"base_surface": "Hard"})
base_surf = s_config["base_surface"]
h2h_surface = h2h_matches[h2h_matches['surface'] == base_surf] if not h2h_matches.empty else pd.DataFrame()

if len(h2h_surface) > 0:
    h2h_a_wins = len(h2h_surface[h2h_surface['winner_clean'] == clean_a])
    h2h_b_wins = len(h2h_surface[h2h_surface['winner_clean'] == clean_b])
    total_h2h = len(h2h_surface)
elif not h2h_matches.empty:
    h2h_a_wins = len(h2h_matches[h2h_matches['winner_clean'] == clean_a])
    h2h_b_wins = len(h2h_matches[h2h_matches['winner_clean'] == clean_b])
    total_h2h = len(h2h_matches)
else:
    h2h_a_wins, h2h_b_wins, total_h2h = 0, 0, 0

score_p4_a = ((h2h_a_wins + 1.0) / (total_h2h + 2.0)) * 100.0
score_p4_b = ((h2h_b_wins + 1.0) / (total_h2h + 2.0)) * 100.0
p4_a, p4_b = score_p4_a * 1.5, score_p4_b * 1.5

# Probability Scaling (Logistic)
rating_a, rating_b = (p1_a + p2_a + p3_a + p4_a), (p1_b + p2_b + p3_b + p4_b)
delta_rating = rating_a - rating_b
prob_a = min(max(1.0 / (1.0 + 10.0 ** (-delta_rating / 280.0)), 0.03), 0.97)
prob_b = 1.0 - prob_a

cote_equitable_a = 1.0 / prob_a
cote_equitable_b = 1.0 / prob_b

# ---------------------------------------------------------
# 6. AFFICHAGE ET LAYOUT PRINCIPAL (SECTION 8)
# ---------------------------------------------------------
st.markdown(f"<div class='cat-title-matchup'>📊 Matchup & Performance sur {surface}</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # CARTE EN-TÊTE JOUEUR A (ROUGE / ROSE)
    st.markdown(f"""
    <div class='player-card-a'>
        <div class='player-header'>
            <div class='player-name-a'>{player_a}</div>
            <div class='style-badge-a'>{stats_a['style']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # GRILLE DE MÉTRIQUES DÉLIMITÉES DANS DES CONTENEURS
    g1, g2 = st.columns(2)
    g1.metric("Win Global", f"{stats_a['overall_winrate']*100:.0f}%")
    g2.metric("Vs Base", f"{stats_a['surface_winrate']*100:.0f}%")
    
    st.write("")
    
    g3, g4 = st.columns(2)
    g3.metric("Forme", f"{stats_a['last_10_wins']}/10")
    g4.metric("Vs Style", f"{winrate_a_vs_b_style*100:.0f}%")

with col2:
    # CARTE EN-TÊTE JOUEUR B (VERT)
    st.markdown(f"""
    <div class='player-card-b'>
        <div class='player-header'>
            <div class='player-name-b'>{player_b}</div>
            <div class='style-badge-b'>{stats_b['style']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # GRILLE DE MÉTRIQUES DÉLIMITÉES DANS DES CONTENEURS
    g1, g2 = st.columns(2)
    g1.metric("Win Global", f"{stats_b['overall_winrate']*100:.0f}%")
    g2.metric("Vs Base", f"{stats_b['surface_winrate']*100:.0f}%")
    
    st.write("")
    
    g3, g4 = st.columns(2)
    g3.metric("Forme", f"{stats_b['last_10_wins']}/10")
    g4.metric("Vs Style", f"{winrate_b_vs_a_style*100:.0f}%")

# BOX D'ANALYSE
fav_surface = player_a if stats_a['surface_winrate'] >= stats_b['surface_winrate'] else player_b
fav_style = player_a if winrate_a_vs_b_style >= winrate_b_vs_a_style else player_b

st.markdown(f"""
<div class='analysis-box'>
    💡 <b>Analyse Matchup ({surface}) :</b> Avantage <b>{fav_surface}</b> sur la base de la surface ({max(stats_a['surface_winrate'], stats_b['surface_winrate'])*100:.0f}% V). Profil tactique favorisé : <b>{fav_style}</b> vs le style adverse ({max(winrate_a_vs_b_style, winrate_b_vs_a_style)*100:.0f}% V).
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. SERVICE & ENGAGEMENT
# ---------------------------------------------------------
st.markdown("<div class='cat-title-service'>⚡ Service & Engagement</div>", unsafe_allow_html=True)

s1, s2 = st.columns(2)

with s1:
    st.markdown(f"<span style='color:#fb7185; font-weight:700;'>🎾 {player_a}</span>", unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    p1.metric("Aces / m", f"{stats_a['avg_aces']:.1f}")
    p2.metric("DF / m", f"{stats_a['avg_dfs']:.1f}")
    st.write("")
    p3, p4 = st.columns(2)
    p3.metric("1st In", f"{stats_a['pct_1st_in']:.0f}%")
    p4.metric("Pts 1st", f"{stats_a['pct_1st_won']:.0f}%")

with s2:
    st.markdown(f"<span style='color:#34d399; font-weight:700;'>🎾 {player_b}</span>", unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    p1.metric("Aces / m", f"{stats_b['avg_aces']:.1f}")
    p2.metric("DF / m", f"{stats_b['avg_dfs']:.1f}")
    st.write("")
    p3, p4 = st.columns(2)
    p3.metric("1st In", f"{stats_b['pct_1st_in']:.0f}%")
    p4.metric("Pts 1st", f"{stats_b['pct_1st_won']:.0f}%")

# ---------------------------------------------------------
# 8. TERMINAL VALUEBET 1N2 (+EV)
# ---------------------------------------------------------
st.markdown("<div class='cat-title-valuebet'>🎯 ValueBet 1N2 (+EV)</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
cote_a = c1.number_input(f"Cote Bookmaker {player_a}", value=float(round(cote_equitable_a, 2)), step=0.05, min_value=1.01)
cote_b = c2.number_input(f"Cote Bookmaker {player_b}", value=float(round(cote_equitable_b, 2)), step=0.05, min_value=1.01)

ev_a = (prob_a * cote_a) - 1.0
ev_b = (prob_b * cote_b) - 1.0

kelly_a = max(0.0, ((cote_a * prob_a) - 1.0) / (cote_a - 1.0)) if cote_a > 1.0 else 0.0
kelly_b = max(0.0, ((cote_b * prob_b) - 1.0) / (cote_b - 1.0)) if cote_b > 1.0 else 0.0

EV_MIN_THRESHOLD = 0.02

r1, r2 = st.columns(2)

with r1:
    css_class = "ev-card-success" if ev_a >= EV_MIN_THRESHOLD else "ev-card-danger"
    st.markdown(f"""
    <div class='{css_class}'>
        <b>{player_a}</b> | Prob : <b>{prob_a*100:.1f}%</b> | Fair : <b>{cote_equitable_a:.2f}</b>
    </div>
    """, unsafe_allow_html=True)
    
    v1, v2 = st.columns(2)
    v1.metric("EV", f"{ev_a*100:+.1f}%")
    v2.metric("Kelly", f"{min(kelly_a*100, 5.0):.1f}% BK")

    if ev_a >= EV_MIN_THRESHOLD:
        st.success(f"🟢 **VALUE BET CONFIRMÉ** (+{ev_a*100:.1f}% EV)")
    elif 0.0 < ev_a < EV_MIN_THRESHOLD:
        st.warning(f"🟡 **MARGE FAIBLE (+{ev_a*100:.1f}%) → NO BET**")
    else:
        st.error("🔴 **Cote trop basse / Pas de Value**")

with r2:
    css_class = "ev-card-success" if ev_b >= EV_MIN_THRESHOLD else "ev-card-danger"
    st.markdown(f"""
    <div class='{css_class}'>
        <b>{player_b}</b> | Prob : <b>{prob_b*100:.1f}%</b> | Fair : <b>{cote_equitable_b:.2f}</b>
    </div>
    """, unsafe_allow_html=True)
    
    v1, v2 = st.columns(2)
    v1.metric("EV", f"{ev_b*100:+.1f}%")
    v2.metric("Kelly", f"{min(kelly_b*100, 5.0):.1f}% BK")

    if ev_b >= EV_MIN_THRESHOLD:
        st.success(f"🟢 **VALUE BET CONFIRMÉ** (+{ev_b*100:.1f}% EV)")
    elif 0.0 < ev_b < EV_MIN_THRESHOLD:
        st.warning(f"🟡 **MARGE FAIBLE (+{ev_b*100:.1f}%) → NO BET**")
    else:
        st.error("🔴 **Cote trop basse / Pas de Value**")
