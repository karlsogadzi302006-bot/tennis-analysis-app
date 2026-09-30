import os
import re
import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Tennis ValueBet AI — Analytics ATP",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# STYLES CSS PERSONNALISÉS
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: #090b10;
        color: #e2e8f0;
    }
    
    /* Titres */
    .main-title {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #64748b;
        font-size: 0.85rem;
        margin-bottom: 20px;
    }

    /* Chiffres des métriques Streamlit */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        color: #94a3b8 !important;
    }

    /* Cartes Joueurs */
    .player-card {
        background: #131722;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 12px;
    }
    
    .player-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .player-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
    }
    
    .style-badge {
        background: rgba(56, 189, 248, 0.1);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Encadrés d'analyse contextuels */
    .analysis-box {
        background: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #38bdf8;
        border-radius: 6px;
        padding: 10px 14px;
        margin-top: 10px;
        margin-bottom: 15px;
        font-size: 0.88rem;
        color: #cbd5e1;
    }

    /* Cartes EV */
    .ev-card-success {
        background: rgba(34, 197, 94, 0.05);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .ev-card-danger {
        background: rgba(239, 68, 68, 0.05);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }

    /* Images ajustées en hauteur */
    [data-testid="stImage"] img {
        border-radius: 10px;
        max-height: 260px;
        width: 100%;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🎾 Tennis ValueBet AI Pro</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Plateforme d'Analyse Prédictive & Détection +EV • ATP Circuit</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. MATRICE DE SIMILARITÉ DES STYLES DE JEU
# ---------------------------------------------------------
STYLE_SIMILARITY = {
    "Gros Serveur":          {"Gros Serveur": 1.0, "Serveur-Volleyeur": 0.8, "Attaquant de Ligne": 0.5, "Polyvalent": 0.3, "Relanceur / Cadenceur": 0.1, "Contreur / Limeur": 0.1},
    "Serveur-Volleyeur":     {"Serveur-Volleyeur": 1.0, "Gros Serveur": 0.8, "Attaquant de Ligne": 0.6, "Polyvalent": 0.4, "Relanceur / Cadenceur": 0.2, "Contreur / Limeur": 0.1},
    "Attaquant de Ligne":    {"Attaquant de Ligne": 1.0, "Polyvalent": 0.7, "Serveur-Volleyeur": 0.6, "Gros Serveur": 0.5, "Relanceur / Cadenceur": 0.4, "Contreur / Limeur": 0.3},
    "Polyvalent":            {"Polyvalent": 1.0, "Attaquant de Ligne": 0.7, "Relanceur / Cadenceur": 0.7, "Serveur-Volleyeur": 0.4, "Contreur / Limeur": 0.5, "Gros Serveur": 0.3},
    "Relanceur / Cadenceur": {"Relanceur / Cadenceur": 1.0, "Contreur / Limeur": 0.8, "Polyvalent": 0.7, "Attaquant de Ligne": 0.4, "Serveur-Volleyeur": 0.2, "Gros Serveur": 0.1},
    "Contreur / Limeur":     {"Contreur / Limeur": 1.0, "Relanceur / Cadenceur": 0.8, "Polyvalent": 0.5, "Attaquant de Ligne": 0.3, "Serveur-Volleyeur": 0.1, "Gros Serveur": 0.1},
}

def clean_name(name):
    if not isinstance(name, str):
        return ""
    cleaned = re.sub(r'[^a-zA-Z\s]', '', name)
    return " ".join(cleaned.lower().split())

def parse_total_games(score_str):
    if not isinstance(score_str, str) or not score_str:
        return np.nan
    sets = re.findall(r'(\d+)-(\d+)', score_str)
    if not sets:
        return np.nan
    total = sum(int(g1) + int(g2) for g1, g2 in sets)
    return total if total >= 12 else np.nan

def parse_sets_count(score_str):
    if not isinstance(score_str, str) or not score_str:
        return np.nan, np.nan
    sets = re.findall(r'(\d+)-(\d+)', score_str)
    if not sets:
        return np.nan, np.nan
    w_sets = sum(1 for g1, g2 in sets if int(g1) > int(g2))
    l_sets = len(sets) - w_sets
    return w_sets, l_sets

# ---------------------------------------------------------
# 2. CHARGEMENT DES CSV SACKMANN
# ---------------------------------------------------------
@st.cache_data
def load_all_local_atp():
    dfs = []
    base_dir = Path(__file__).resolve().parent
    raw_files = list(base_dir.glob("atp_matches_*.csv")) + list(Path(".").glob("atp_matches_*.csv"))
    unique_paths = set(p.resolve() for p in raw_files)

    for filepath in unique_paths:
        try:
            df = pd.read_csv(filepath, low_memory=False, on_bad_lines='skip')
            df.columns = [str(c).strip().lower() for c in df.columns]

            if 'winner_name' not in df.columns or 'loser_name' not in df.columns:
                continue

            sub = pd.DataFrame()
            sub['winner_name'] = df['winner_name'].astype(str).str.strip()
            sub['loser_name'] = df['loser_name'].astype(str).str.strip()

            if 'tourney_date' in df.columns:
                sub['tourney_date'] = pd.to_datetime(df['tourney_date'].astype(str), format='%Y%m%d', errors='coerce')
            else:
                sub['tourney_date'] = pd.Timestamp.now()

            sub['tourney_name'] = df['tourney_name'].astype(str) if 'tourney_name' in df.columns else "Tournoi ATP"
            sub['surface'] = df['surface'].astype(str).str.capitalize() if 'surface' in df.columns else "Hard"
            sub['round'] = df['round'].astype(str) if 'round' in df.columns else "R32"
            sub['score'] = df['score'].astype(str) if 'score' in df.columns else ""

            stat_cols = ['w_ace', 'w_df', 'w_svpt', 'w_1stin', 'w_1stwon', 'w_2ndwon',
                         'l_ace', 'l_df', 'l_svpt', 'l_1stin', 'l_1stwon', 'l_2ndwon']
            
            for sc in stat_cols:
                sub[sc] = pd.to_numeric(df[sc], errors='coerce') if sc in df.columns else np.nan

            dfs.append(sub)
        except Exception:
            pass

    if not dfs:
        return pd.DataFrame()

    full_df = pd.concat(dfs, ignore_index=True)
    full_df = full_df[full_df['winner_name'].str.len() > 2]
    full_df = full_df[full_df['loser_name'].str.len() > 2]
    full_df = full_df.drop_duplicates(subset=['tourney_date', 'winner_name', 'loser_name', 'score'])

    full_df['winner_clean'] = full_df['winner_name'].apply(clean_name)
    full_df['loser_clean'] = full_df['loser_name'].apply(clean_name)
    full_df['total_games'] = full_df['score'].apply(parse_total_games)

    return full_df.sort_values(by='tourney_date', ascending=False)

df_circuit = load_all_local_atp()

if df_circuit.empty:
    st.error("⚠️ Impossible d'extraire les données des fichiers CSV.")
    st.stop()

st.sidebar.success(f"⚡ {len(df_circuit)} matchs ATP chargés !")

# ---------------------------------------------------------
# 3. SELECTION DES JOUEURS
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ Configuration du Match")

all_players = sorted(list(set(df_circuit['winner_name'].unique()).union(set(df_circuit['loser_name'].unique()))))

player_a = st.sidebar.selectbox("🎾 Joueur A", all_players, index=0)
default_b_idx = 1 if len(all_players) > 1 else 0
player_b = st.sidebar.selectbox("🎾 Joueur B", all_players, index=default_b_idx)

surface = st.sidebar.selectbox("🌱 Surface de jeu", ["Hard", "Clay", "Grass"])

# ---------------------------------------------------------
# 4. CALCULS METRIQUES & STYLES (FILTRÉS PAR SURFACE)
# ---------------------------------------------------------
def get_player_matches(df, player_name):
    c_name = clean_name(player_name)
    wins = df[df['winner_clean'] == c_name]
    losses = df[df['loser_clean'] == c_name]
    return wins, losses

def categorize_player_style(ace_per_match, pct_first_won, pct_second_won):
    if ace_per_match >= 7.5:
        return "Gros Serveur"
    elif ace_per_match >= 4.5 and pct_first_won >= 0.73:
        return "Serveur-Volleyeur"
    elif pct_first_won >= 0.69 and ace_per_match >= 3.0:
        return "Attaquant de Ligne"
    elif pct_first_won <= 0.61 and pct_second_won <= 0.48:
        return "Contreur / Limeur"
    elif pct_first_won <= 0.64:
        return "Relanceur / Cadenceur"
    else:
        return "Polyvalent"

@st.cache_data
def build_all_player_styles(df_sub):
    styles = {}
    w = df_sub[['winner_name', 'w_ace', 'w_svpt', 'w_1stwon', 'w_2ndwon']].rename(
        columns={'winner_name': 'player', 'w_ace': 'ace', 'w_svpt': 'svpt', 'w_1stwon': 'first', 'w_2ndwon': 'second'})
    l = df_sub[['loser_name', 'l_ace', 'l_svpt', 'l_1stwon', 'l_2ndwon']].rename(
        columns={'loser_name': 'player', 'l_ace': 'ace', 'l_svpt': 'svpt', 'l_1stwon': 'first', 'l_2ndwon': 'second'})
    
    combined = pd.concat([w, l], ignore_index=True)
    grouped = combined.groupby('player').agg({'ace': 'mean', 'svpt': 'sum', 'first': 'sum', 'second': 'sum', 'player': 'count'})
    
    for player, row in grouped.iterrows():
        if row['player'] < 3:
            styles[player] = "Polyvalent"
            continue
        pct_1st = (row['first'] / row['svpt']) if row['svpt'] > 0 else 0.65
        pct_2nd = (row['second'] / row['svpt']) if row['svpt'] > 0 else 0.50
        styles[player] = categorize_player_style(row['ace'], pct_1st, pct_2nd)
        
    return styles

player_styles_map = build_all_player_styles(df_circuit)

def get_detailed_metrics(player, surface_match):
    p_wins, p_losses = get_player_matches(df_circuit, player)
    total_m = len(p_wins) + len(p_losses)
    if total_m == 0:
        return None

    overall_winrate = len(p_wins) / total_m
    all_matches = pd.concat([p_wins.assign(is_win=1), p_losses.assign(is_win=0)]).sort_values(by='tourney_date', ascending=False)
    last_10 = all_matches.head(10)
    recent_form = last_10['is_win'].mean() if len(last_10) > 0 else 0.5
    
    # MATCHS SUR LA SURFACE SPECIFIQUE
    surf_wins = p_wins[p_wins['surface'] == surface_match]
    surf_losses = p_losses[p_losses['surface'] == surface_match]
    surf_matches = pd.concat([surf_wins.assign(is_win=1), surf_losses.assign(is_win=0)]).sort_values(by='tourney_date', ascending=False)
    
    total_surf = len(surf_matches)
    surface_winrate = len(surf_wins) / total_surf if total_surf >= 3 else overall_winrate
    
    # Utiliser les matchs sur la surface si suffisants, sinon l'historique récent global
    target_matches = surf_matches.head(12) if total_surf >= 5 else all_matches.head(12)
    
    titles = len(p_wins[p_wins['round'].astype(str).str.upper().isin(['F', 'THE FINAL', 'FINAL'])])
    
    # Extraction des stats Ace & DF sur la surface ciblée
    w_surf = target_matches[target_matches['is_win'] == 1]
    l_surf = target_matches[target_matches['is_win'] == 0]
    
    aces = pd.concat([w_surf['w_ace'], l_surf['l_ace']]).dropna()
    dfs_count = pd.concat([w_surf['w_df'], l_surf['l_df']]).dropna()
    
    svpt = pd.concat([w_surf['w_svpt'], l_surf['l_svpt']]).sum()
    fst_in = pd.concat([w_surf['w_1stin'], l_surf['l_1stin']]).sum()
    fst_won = pd.concat([w_surf['w_1stwon'], l_surf['l_1stwon']]).sum()
    
    pct_1st_in = (fst_in / svpt * 100) if svpt > 0 else 60.0
    pct_1st_won = (fst_won / fst_in * 100) if fst_in > 0 else 70.0

    avg_games_surf = target_matches['total_games'].dropna().mean()
    
    three_sets_count = 0
    tb_count = 0
    valid_scores_count = 0
    for s_str in target_matches['score']:
        w_s, l_s = parse_sets_count(s_str)
        if not np.isnan(w_s) and (w_s + l_s) >= 2:
            valid_scores_count += 1
            if (w_s + l_s) >= 3:
                three_sets_count += 1
        if "7-6" in str(s_str) or "6-7" in str(s_str):
            tb_count += 1

    pct_3_sets = (three_sets_count / valid_scores_count * 100) if valid_scores_count > 0 else 30.0
    pct_tb = (tb_count / len(target_matches) * 100) if len(target_matches) > 0 else 20.0

    return {
        "player_name": player, "overall_winrate": overall_winrate, "recent_form": recent_form,
        "surface_winrate": surface_winrate, "style": player_styles_map.get(player, "Polyvalent"),
        "total_matches": total_m, "total_wins": len(p_wins), "total_losses": len(p_losses),
        "total_surf_matches": total_surf,
        "last_10_wins": int(recent_form * len(last_10)), "titles": titles,
        "avg_aces": aces.mean() if len(aces) > 0 else 0.0,
        "avg_dfs": dfs_count.mean() if len(dfs_count) > 0 else 0.0,
        "pct_1st_in": pct_1st_in, "pct_1st_won": pct_1st_won,
        "avg_games": avg_games_surf if not np.isnan(avg_games_surf) else 22.0,
        "pct_3_sets": pct_3_sets, "pct_tb": pct_tb,
        "p_wins": p_wins, "p_losses": p_losses
    }

stats_a = get_detailed_metrics(player_a, surface)
stats_b = get_detailed_metrics(player_b, surface)

if not stats_a or not stats_b:
    st.warning("Données insuffisantes pour l'un des joueurs.")
    st.stop()

# ---------------------------------------------------------
# 5. H2H & ESTIMATION MODÈLE
# ---------------------------------------------------------
def get_weighted_winrate_vs_style(stats_player, target_style):
    weighted_wins, weighted_total = 0.0, 0.0
    for opp in stats_player['p_wins']['loser_name']:
        sim_score = STYLE_SIMILARITY[target_style].get(player_styles_map.get(opp, "Polyvalent"), 0.3)
        weighted_wins += 1.0 * sim_score
        weighted_total += 1.0 * sim_score
    for opp in stats_player['p_losses']['winner_name']:
        sim_score = STYLE_SIMILARITY[target_style].get(player_styles_map.get(opp, "Polyvalent"), 0.3)
        weighted_total += 1.0 * sim_score
    return (weighted_wins / weighted_total) if weighted_total >= 1.0 else stats_player['overall_winrate']

winrate_a_vs_b_style = get_weighted_winrate_vs_style(stats_a, stats_b['style'])
winrate_b_vs_a_style = get_weighted_winrate_vs_style(stats_b, stats_a['style'])

clean_a, clean_b = clean_name(player_a), clean_name(player_b)
h2h_matches = df_circuit[
    ((df_circuit['winner_clean'] == clean_a) & (df_circuit['loser_clean'] == clean_b)) |
    ((df_circuit['winner_clean'] == clean_b) & (df_circuit['loser_clean'] == clean_a))
].copy()

h2h_a_wins = len(h2h_matches[h2h_matches['winner_clean'] == clean_a])
h2h_b_wins = len(h2h_matches[h2h_matches['winner_clean'] == clean_b])
total_h2h = len(h2h_matches)

score_a = (stats_a['surface_winrate'] * 0.30) + (winrate_a_vs_b_style * 0.25) + (stats_a['recent_form'] * 0.25) + (stats_a['overall_winrate'] * 0.20)
score_b = (stats_b['surface_winrate'] * 0.30) + (winrate_b_vs_a_style * 0.25) + (stats_b['recent_form'] * 0.25) + (stats_b['overall_winrate'] * 0.20)

prob_est_a = (score_a * 0.80) + ((h2h_a_wins / total_h2h) * 0.20) if total_h2h > 0 else score_a
prob_a = prob_est_a / (score_a + score_b)
prob_b = 1.0 - prob_a
cote_equitable_a, cote_equitable_b = 1 / prob_a, 1 / prob_b

# ---------------------------------------------------------
# 6. AFFICHAGE : CARTES COMPARATIVES ET DUEL
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class='player-card'>
        <div class='player-header'>
            <div class='player-name'>{player_a}</div>
            <div class='style-badge'>{stats_a['style']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Winrate Global", f"{stats_a['overall_winrate']*100:.1f}%")
    m2.metric(f"Sur {surface}", f"{stats_a['surface_winrate']*100:.1f}%")
    m3.metric("Forme (10d)", f"{stats_a['last_10_wins']}/10 V")
    m4.metric(f"Vs '{stats_b['style']}'", f"{winrate_a_vs_b_style*100:.1f}%")

with col2:
    st.markdown(f"""
    <div class='player-card'>
        <div class='player-header'>
            <div class='player-name'>{player_b}</div>
            <div class='style-badge'>{stats_b['style']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Winrate Global", f"{stats_b['overall_winrate']*100:.1f}%")
    m2.metric(f"Sur {surface}", f"{stats_b['surface_winrate']*100:.1f}%")
    m3.metric("Forme (10d)", f"{stats_b['last_10_wins']}/10 V")
    m4.metric(f"Vs '{stats_a['style']}'", f"{winrate_b_vs_a_style*100:.1f}%")

# MINI-TEXTE : FAVORITISME SURFACE & FORME
fav_surface = player_a if stats_a['surface_winrate'] >= stats_b['surface_winrate'] else player_b
fav_form = player_a if stats_a['recent_form'] >= stats_b['recent_form'] else player_b
st.markdown(f"""
<div class='analysis-box'>
    💡 <b>Analyse Surface & Forme :</b> Sur <b>{surface}</b>, l'avantage va à <b>{fav_surface}</b> ({max(stats_a['surface_winrate'], stats_b['surface_winrate'])*100:.1f}% de victoires sur cette surface). 
    En terme de forme récente sur les 10 derniers matchs, <b>{fav_form}</b> prend le dessus.
</div>
""", unsafe_allow_html=True)

# BANNIÈRE 1
st.image("https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?q=80&w=1200&auto=format&fit=crop", use_container_width=True)

# ---------------------------------------------------------
# 7. METRIQUES COMPACTES STYLE DE JEU
# ---------------------------------------------------------
st.subheader("📊 Profils & Service / Engagement")

s1, s2 = st.columns(2)
with s1:
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Aces/m", f"{stats_a['avg_aces']:.1f}")
    p2.metric("DF/m", f"{stats_a['avg_dfs']:.1f}")
    p3.metric("1ère In", f"{stats_a['pct_1st_in']:.1f}%")
    p4.metric("Pts 1ère", f"{stats_a['pct_1st_won']:.1f}%")

with s2:
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Aces/m", f"{stats_b['avg_aces']:.1f}")
    p2.metric("DF/m", f"{stats_b['avg_dfs']:.1f}")
    p3.metric("1ère In", f"{stats_b['pct_1st_in']:.1f}%")
    p4.metric("Pts 1ère", f"{stats_b['pct_1st_won']:.1f}%")

# MINI-TEXTE : FAVORITISME SERVICE
fav_serve = player_a if stats_a['pct_1st_won'] >= stats_b['pct_1st_won'] else player_b
st.markdown(f"""
<div class='analysis-box'>
    ⚡ <b>Analyse au Service sur {surface} :</b> <b>{fav_serve}</b> possède le service le plus percutant avec <b>{max(stats_a['pct_1st_won'], stats_b['pct_1st_won']):.1f}%</b> de points gagnés derrière sa 1ère balle. 
    Ce facteur est déterminant pour réduire le nombre de breaks concédés.
</div>
""", unsafe_allow_html=True)

# BANNIÈRE 2
st.image("https://images.unsplash.com/photo-1530915534664-4ac6423ca938?q=80&w=1200&auto=format&fit=crop", use_container_width=True)

# ---------------------------------------------------------
# 8. CONFRONTATIONS DIRECTES (H2H)
# ---------------------------------------------------------
st.subheader("⚔️ Face-à-Face Direct (H2H)")
if total_h2h > 0:
    st.info(f"Historique direct : **{player_a}** **{h2h_a_wins}** — **{h2h_b_wins}** **{player_b}** ({total_h2h} duels)")
    fav_h2h = player_a if h2h_a_wins > h2h_b_wins else (player_b if h2h_b_wins > h2h_a_wins else "Égalité")
    st.markdown(f"""
    <div class='analysis-box'>
        🤝 <b>Analyse H2H :</b> <b>{fav_h2h}</b> mène l'historique direct des duels sur le circuit ATP ({max(h2h_a_wins, h2h_b_wins)} victoires sur {total_h2h} matchs).
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 Voir la liste des duels"):
        st.dataframe(
            h2h_matches[['tourney_date', 'tourney_name', 'surface', 'round', 'winner_name', 'score']]
            .rename(columns={'tourney_date': 'Date', 'tourney_name': 'Tournoi', 'winner_name': 'Vainqueur', 'round': 'Tour', 'score': 'Score'}),
            use_container_width=True
        )
else:
    st.write("Aucune confrontation directe enregistrée entre ces deux joueurs.")
    st.markdown(f"""
    <div class='analysis-box'>
        ℹ️ <b>Analyse H2H :</b> Premier duel officiel entre ces deux joueurs. Le modèle se base à 100% sur la forme, le style et la surface.
    </div>
    """, unsafe_allow_html=True)

# BANNIÈRE 3
st.image("https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?q=80&w=1200&auto=format&fit=crop", use_container_width=True)

# ---------------------------------------------------------
# 9. DETECTEUR +EV ET CALCULATEUR VALUEBET
# ---------------------------------------------------------
st.subheader("🎯 ValueBet & Cotes 1N2 (+EV)")

c1, c2 = st.columns(2)
cote_a = c1.number_input(f"Cote {player_a}", value=float(round(cote_equitable_a, 2)), step=0.05)
cote_b = c2.number_input(f"Cote {player_b}", value=float(round(cote_equitable_b, 2)), step=0.05)

ev_a = (prob_a * cote_a) - 1
ev_b = (prob_b * cote_b) - 1

kelly_a = max(0.0, ((cote_a * prob_a) - 1) / (cote_a - 1)) if cote_a > 1 else 0
kelly_b = max(0.0, ((cote_b * prob_b) - 1) / (cote_b - 1)) if cote_b > 1 else 0

r1, r2 = st.columns(2)

with r1:
    css_class = "ev-card-success" if ev_a > 0 else "ev-card-danger"
    st.markdown(f"""
    <div class='{css_class}'>
        <b>{player_a}</b> | Prob : <b>{prob_a*100:.1f}%</b> | Cote Fair : <b>{cote_equitable_a:.2f}</b>
    </div>
    """, unsafe_allow_html=True)
    
    v1, v2 = st.columns(2)
    v1.metric("EV (+EV)", f"{ev_a*100:+.1f}%")
    v2.metric("Kelly", f"{min(kelly_a*100, 5.0):.1f}% BK")

    if ev_a > 0:
        st.success(f"🟢 **VALUE BET SUR {player_a}** (+{ev_a*100:.1f}% EV)")
    else:
        st.error("🔴 **Cote trop basse**")

with r2:
    css_class = "ev-card-success" if ev_b > 0 else "ev-card-danger"
    st.markdown(f"""
    <div class='{css_class}'>
        <b>{player_b}</b> | Prob : <b>{prob_b*100:.1f}%</b> | Cote Fair : <b>{cote_equitable_b:.2f}</b>
    </div>
    """, unsafe_allow_html=True)
    
    v1, v2 = st.columns(2)
    v1.metric("EV (+EV)", f"{ev_b*100:+.1f}%")
    v2.metric("Kelly", f"{min(kelly_b*100, 5.0):.1f}% BK")

    if ev_b > 0:
        st.success(f"🟢 **VALUE BET SUR {player_b}** (+{ev_b*100:.1f}% EV)")
    else:
        st.error("🔴 **Cote trop basse**")

# BANNIÈRE 4
st.image("https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff?q=80&w=1200&auto=format&fit=crop", use_container_width=True)

# ---------------------------------------------------------
# 10. ANALYSE AFFINÉE DES MARCHÉS ANNEXES
# ---------------------------------------------------------
st.subheader(f"🔥 Analyse Détaillée des Marchés Annexes sur {surface}")

# Calculs prédictifs filtrés
combined_avg_games = (stats_a['avg_games'] + stats_b['avg_games']) / 2
combined_3set_pct = (stats_a['pct_3_sets'] + stats_b['pct_3_sets']) / 2
combined_tb_pct = (stats_a['pct_tb'] + stats_b['pct_tb']) / 2

total_projected_aces = stats_a['avg_aces'] + stats_b['avg_aces']
total_projected_dfs = stats_a['avg_dfs'] + stats_b['avg_dfs']

both_big_servers = (stats_a['style'] in ["Gros Serveur", "Serveur-Volleyeur"]) and (stats_b['style'] in ["Gros Serveur", "Serveur-Volleyeur"])
both_returners = (stats_a['style'] in ["Relanceur / Cadenceur", "Contreur / Limeur"]) and (stats_b['style'] in ["Relanceur / Cadenceur", "Contreur / Limeur"])

# Facteurs de domination et d'instabilité
prob_fav = max(prob_a, prob_b)
fav_player_name = player_a if prob_a > prob_b else player_b
underdog_player_name = player_b if prob_a > prob_b else player_a

is_heavy_blowout = (prob_fav >= 0.72) or (abs(stats_a['surface_winrate'] - stats_b['surface_winrate']) >= 0.30)
is_unstable_match = (stats_a['avg_dfs'] >= 4.5 or stats_b['avg_dfs'] >= 4.5) and (combined_3set_pct < 30)

m1_col, m2_col = st.columns(2)

with m1_col:
    # 1. OVER / UNDER JEUX
    with st.container(border=True):
        st.markdown(f"#### 🎾 Over / Under Jeux (Spécifique {surface})")
        
        j1, j2, j3 = st.columns(3)
        j1.metric("Moy. Jeux/m", f"{combined_avg_games:.1f}")
        j2.metric("Chances 3 Sets", f"{combined_3set_pct:.1f}%")
        j3.metric("Freq. Tie-Break", f"{combined_tb_pct:.1f}%")

        if is_heavy_blowout:
            st.error(f"🔴 **DANGER OVER / PRÉVISION UNDER 21.5 JEUX**\n\n"
                     f"• **Analyse de sur-domination :** **{fav_fav_name if 'fav_fav_name' in locals() else fav_player_name}** possède une trop grande marge sur {surface} ({prob_fav*100:.1f}% de chances). "
                     f"Risque élevé de victoire expéditive (ex: 6-3, 6-2). L'Over est déconseillé.")
        elif is_unstable_match:
            st.warning("⚠️ **OVER TRÈS RISQUÉ / INCONSTANCE**\n\n"
                       f"• **Analyse d'instabilité :** Nombreuses doubles fautes et fautes directes au service ({total_projected_dfs:.1f} DF/m cumulées). "
                       f"Les breaks sont fréquents, empêchant les sets de monter en 6-6/7-5.")
        elif combined_avg_games >= 23.0 or both_big_servers or combined_3set_pct >= 45:
            st.success("🟢 **RECOMMANDATION : OVER 22.5 JEUX**\n\n"
                       f"• **Analyse :** Profils équilibrés sur {surface} avec un fort taux d'accrochage ({combined_3set_pct:.0f}% de 3ème set). "
                       f"Match serré en perspective.")
        elif combined_avg_games <= 20.5 or both_returners:
            st.warning("⚡ **RECOMMANDATION : UNDER 21.5 JEUX**\n\n"
                       f"• **Analyse :** Deux profil de relanceurs/cont reurs. Breaks réguliers projetés ramenant la moyenne sous 21 jeux.")
        else:
            st.info("🔵 **PAS DE BET RECOMMANDÉ (MARCHÉ NEUTRE)**\n\n• Les statistiques ne montrent aucun edge évident sur le cut de jeux.")

    # 2. OVER / UNDER ACES
    with st.container(border=True):
        st.markdown(f"#### 💥 Over / Under Aces (Spécifique {surface})")
        
        a1, a2, a3 = st.columns(3)
        a1.metric(f"Aces {player_a}", f"{stats_a['avg_aces']:.1f}")
        a2.metric(f"Aces {player_b}", f"{stats_b['avg_aces']:.1f}")
        a3.metric("Total Projeté", f"{total_projected_aces:.1f}")

        # Détermination dynamique de la ligne de cut
        baseline_aces = 14.5 if surface == "Grass" else (11.5 if surface == "Hard" else 7.5)
        
        if total_projected_aces >= (baseline_aces + 2.0):
            st.success(f"🟢 **RECOMMANDATION : OVER {baseline_aces:.1f} ACES**\n\n"
                       f"• **Analyse :** Gros serveurs réguliers sur **{surface}**. "
                       f"Projection solide de `{total_projected_aces:.1f}` aces au total.")
        elif total_projected_aces <= (baseline_aces - 2.0) or surface == "Clay":
            st.error(f"🔴 **RECOMMANDATION : UNDER {baseline_aces:.1f} ACES**\n\n"
                     f"• **Analyse :** Qualité de relance ou surface lente ({surface}) freinant le nombre d'aces. "
                     f"Projection à seulement `{total_projected_aces:.1f}` aces.")
        else:
            st.info(f"🔵 **MARCHÉ ÉQUILIBRÉ SUR LES ACES** (Cut estimé : {round(total_projected_aces) - 0.5:.1f} Aces)")

with m2_col:
    # 3. OVER / UNDER DOUBLES FAUTES
    with st.container(border=True):
        st.markdown(f"#### ⚠️ Over / Under Doubles Fautes (Sur {surface})")
        
        df1, df2, df3 = st.columns(3)
        df1.metric(f"DF {player_a}", f"{stats_a['avg_dfs']:.1f}")
        df2.metric(f"DF {player_b}", f"{stats_b['avg_dfs']:.1f}")
        df3.metric("Total Projeté", f"{total_projected_dfs:.1f}")

        if total_projected_dfs >= 6.5:
            st.warning(f"⚡ **PRÉVISION : OVER 6.5 DOUBLES FAUTES**\n\n"
                       f"• **Analyse :** Prise de risque excessive ou fébrilité sur 2nde balle ({total_projected_dfs:.1f} DF/m en moyenne).")
        elif total_projected_dfs <= 4.0:
            st.success(f"🟢 **PRÉVISION : UNDER 5.5 DOUBLES FAUTES**\n\n"
                       f"• **Analyse :** Deux joueurs très réguliers au service sur {surface} avec peu de déchet sur 2nde balle.")
        else:
            st.info("🔵 **MARCHÉ NEUTRE SUR LES DOUBLES FAUTES**")

    # 4. HANDICAP SETS
    with st.container(border=True):
        st.markdown(f"#### 🛡️ Handicap Sets (+1.5 / -1.5 Sets)")
        
        out_stats = stats_b if prob_a > prob_b else stats_a

        st.write(f"• **Favori Modèle :** `{fav_player_name}` ({prob_fav*100:.1f}% de chances)")
        
        if is_heavy_blowout:
            st.success(f"🚀 **SAFE : {fav_player_name} à -1.5 Sets (Victoire 2-0 / 3-0)**\n\n"
                       f"• **Analyse :** Ecart de niveau prononcé sur {surface}. Le favori ne devrait pas concéder de set.")
        elif combined_3set_pct >= 35 or (0.50 <= prob_fav <= 0.65):
            st.success(f"🛡️ **SAFE : {underdog_player_name} à +1.5 Sets**\n\n"
                       f"• **Analyse :** Match serré. **{underdog_player_name}** accroche un set dans {out_stats['pct_3_sets']:.0f}% de ses matchs récents.")
        else:
            st.info(f"🔵 **Victoire sèche recommandée** sur {fav_player_name}")