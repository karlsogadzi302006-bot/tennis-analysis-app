import os
import re
import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuration obligatoire TOUT EN HAUT
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* FOND LUXE SOMBRE AVEC MOTIF DISCRET */
    .stApp {
        background-color: #07090e;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(30, 41, 59, 0.3) 0%, transparent 70%),
            radial-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 0);
        background-size: 100% 100%, 20px 20px;
        color: #f8fafc;
    }
    
    /* EN-TÊTE PRINCIPAL */
    .main-title {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #64748b;
        font-size: 0.82rem !important;
        margin-bottom: 20px;
        font-weight: 500;
    }

    /* TITRES DE CATÉGORIES PERSONNALISÉS PAR COULEUR */
    .cat-title-matchup {
        color: #fb7185 !important;
        font-size: 1.25rem; font-weight: 800; margin-top: 18px; margin-bottom: 10px;
        border-bottom: 2px solid rgba(251, 113, 133, 0.4); padding-bottom: 4px;
    }
    .cat-title-service {
        color: #38bdf8 !important;
        font-size: 1.25rem; font-weight: 800; margin-top: 22px; margin-bottom: 10px;
        border-bottom: 2px solid rgba(56, 189, 248, 0.4); padding-bottom: 4px;
    }
    .cat-title-h2h {
        color: #c084fc !important;
        font-size: 1.25rem; font-weight: 800; margin-top: 22px; margin-bottom: 10px;
        border-bottom: 2px solid rgba(192, 132, 252, 0.4); padding-bottom: 4px;
    }
    .cat-title-valuebet {
        color: #f59e0b !important;
        font-size: 1.25rem; font-weight: 800; margin-top: 22px; margin-bottom: 10px;
        border-bottom: 2px solid rgba(245, 158, 11, 0.4); padding-bottom: 4px;
    }
    .cat-title-annexes {
        color: #34d399 !important;
        font-size: 1.25rem; font-weight: 800; margin-top: 22px; margin-bottom: 10px;
        border-bottom: 2px solid rgba(52, 211, 153, 0.4); padding-bottom: 4px;
    }

    /* CARTES JOUEURS EN-TÊTE */
    .player-card-a {
        background: linear-gradient(145deg, rgba(244, 63, 94, 0.12) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1.5px solid #f43f5e;
        box-shadow: 0 0 10px rgba(244, 63, 94, 0.15);
        border-radius: 12px; padding: 10px 14px; margin-bottom: 10px;
    }
    .player-card-b {
        background: linear-gradient(145deg, rgba(52, 211, 153, 0.12) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1.5px solid #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
        border-radius: 12px; padding: 10px 14px; margin-bottom: 10px;
    }
    .player-name-a { font-size: 1.1rem !important; font-weight: 800; color: #fb7185; }
    .player-name-b { font-size: 1.1rem !important; font-weight: 800; color: #34d399; }
    
    .style-badge-a {
        background: rgba(244, 63, 94, 0.2); color: #fecdd3; border: 1px solid rgba(244, 63, 94, 0.5);
        padding: 3px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700;
    }
    .style-badge-b {
        background: rgba(16, 185, 129, 0.2); color: #a7f3d0; border: 1px solid rgba(16, 185, 129, 0.5);
        padding: 3px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700;
    }

    /* --- DÉLIMITATION STRICTE DES CASES DE METRIQUES --- */
    [data-testid="stMetric"] {
        background: #111827 !important; /* Fond plus foncé et bien distinct */
        border-radius: 10px !important;
        padding: 8px 6px !important;
        text-align: center !important;
        margin-bottom: 8px !important;
    }

    /* Bordure Rose/Titanium pour les métriques Matchup */
    .card-matchup [data-testid="stMetric"] {
        border: 1.5px solid rgba(251, 113, 133, 0.4) !important;
        box-shadow: 0 2px 8px rgba(251, 113, 133, 0.08) !important;
    }
    .card-matchup [data-testid="stMetricValue"] { color: #fbbf24 !important; }

    /* Bordure Cyan pour les métriques Service */
    .card-service [data-testid="stMetric"] {
        border: 1.5px solid rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 2px 8px rgba(56, 189, 248, 0.08) !important;
    }
    .card-service [data-testid="stMetricValue"] { color: #38bdf8 !important; }

    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important; font-weight: 800 !important; line-height: 1.2 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important; font-weight: 700 !important; color: #cbd5e1 !important;
        white-space: normal !important; word-break: break-word !important;
    }

    /* BOÎTES D'ANALYSE */
    .analysis-box {
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(251, 191, 36, 0.4);
        border-left: 4px solid #fbbf24;
        border-radius: 8px; padding: 12px; margin-top: 8px; margin-bottom: 16px;
        font-size: 0.85rem !important; line-height: 1.4 !important; color: #f1f5f9;
    }

    /* VALUEBET CARDS AVEC BORDURES FORTES */
    .ev-card-success {
        background: rgba(16, 185, 129, 0.12);
        border: 1.5px solid #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
        border-radius: 10px; padding: 12px; margin-bottom: 10px;
    }
    .ev-card-danger {
        background: rgba(239, 68, 68, 0.12);
        border: 1.5px solid #ef4444;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.15);
        border-radius: 10px; padding: 12px; margin-bottom: 10px;
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
# 2. SELECTION DES 11 SOUS-SURFACES TENNISTIQUES
# ---------------------------------------------------------
SURFACE_VARIATIONS = [
    "Dur rapide",
    "Dur moyen",
    "Dur lent",
    "Dur intérieur / Moquette",
    "Terre battue ocre classique",
    "Terre battue verte (Har-Tru)",
    "Terre battue synthétique",
    "Gazon naturel rapide",
    "Gazon naturel lent (Wimbledon)",
    "Gazon synthétique"
]

# Coefficients d'impact tactique par sous-surface
SURFACE_FACTORS = {
    "Dur rapide":                   {"serve_weight": 1.30, "return_weight": 0.80, "base_surface": "Hard"},
    "Dur moyen":                    {"serve_weight": 1.00, "return_weight": 1.00, "base_surface": "Hard"},
    "Dur lent":                     {"serve_weight": 0.85, "return_weight": 1.15, "base_surface": "Hard"},
    "Dur intérieur / Moquette":     {"serve_weight": 1.35, "return_weight": 0.75, "base_surface": "Hard"},
    "Terre battue ocre classique":  {"serve_weight": 0.70, "return_weight": 1.30, "base_surface": "Clay"},
    "Terre battue verte (Har-Tru)": {"serve_weight": 0.80, "return_weight": 1.20, "base_surface": "Clay"},
    "Terre battue synthétique":     {"serve_weight": 0.85, "return_weight": 1.15, "base_surface": "Clay"},
    "Gazon naturel rapide":         {"serve_weight": 1.40, "return_weight": 0.70, "base_surface": "Grass"},
    "Gazon naturel lent (Wimbledon)":{"serve_weight": 1.10, "return_weight": 0.95, "base_surface": "Grass"},
    "Gazon synthétique":            {"serve_weight": 1.25, "return_weight": 0.80, "base_surface": "Grass"}
}

# ---------------------------------------------------------
# 3. SELECTION EN BARRE LATÉRALE
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ Configuration du Match")

all_players = sorted(list(set(df_circuit['winner_name'].unique()).union(set(df_circuit['loser_name'].unique()))))

player_a = st.sidebar.selectbox("🎾 Joueur A", all_players, index=0)
default_b_idx = 1 if len(all_players) > 1 else 0
player_b = st.sidebar.selectbox("🎾 Joueur B", all_players, index=default_b_idx)

surface = st.sidebar.selectbox("🌱 Surface spécifique", SURFACE_VARIATIONS)

# ---------------------------------------------------------
# 4. CALCUL DES METRIQUES AVEC AJUSTEMENT PAR SOUS-SURFACE
# ---------------------------------------------------------
LEVEL_WEIGHTS = {'G': 1.6, 'M': 1.4, 'A': 1.2, 'C': 0.75, 'S': 0.6, 'D': 0.5}

def get_detailed_metrics(player, detailed_surface):
    s_config = SURFACE_FACTORS.get(detailed_surface, {"serve_weight": 1.0, "return_weight": 1.0, "base_surface": "Hard"})
    base_surf = s_config["base_surface"]
    
    p_wins, p_losses = get_player_matches(df_circuit, player)
    total_m = len(p_wins) + len(p_losses)
    if total_m == 0:
        return None

    w_levels = p_wins['tourney_level'].map(LEVEL_WEIGHTS).fillna(1.0) if len(p_wins) > 0 else pd.Series([1.0])
    l_levels = p_losses['tourney_level'].map(LEVEL_WEIGHTS).fillna(1.0) if len(p_losses) > 0 else pd.Series([1.0])
    
    avg_tourney_level = (w_levels.sum() + l_levels.sum()) / total_m if total_m > 0 else 1.0

    overall_winrate = len(p_wins) / total_m
    all_matches = pd.concat([p_wins.assign(is_win=1), p_losses.assign(is_win=0)]).sort_values(by='tourney_date', ascending=False)
    last_10 = all_matches.head(10)
    recent_form = last_10['is_win'].mean() if len(last_10) > 0 else 0.5
    
    surf_wins = p_wins[p_wins['surface'] == base_surf]
    surf_losses = p_losses[p_losses['surface'] == base_surf]
    surf_matches = pd.concat([surf_wins.assign(is_win=1), surf_losses.assign(is_win=0)]).sort_values(by='tourney_date', ascending=False)
    
    total_surf = len(surf_matches)
    surface_winrate = len(surf_wins) / total_surf if total_surf >= 3 else overall_winrate
    
    target_matches = surf_matches.head(12) if total_surf >= 5 else all_matches.head(12)
    
    w_surf = target_matches[target_matches['is_win'] == 1]
    l_surf = target_matches[target_matches['is_win'] == 0]
    
    aces = pd.concat([w_surf['w_ace'], l_surf['l_ace']]).dropna() if ('w_ace' in w_surf.columns and 'l_ace' in l_surf.columns) else pd.Series([0])
    dfs_count = pd.concat([w_surf['w_df'], l_surf['l_df']]).dropna() if ('w_df' in w_surf.columns and 'l_df' in l_surf.columns) else pd.Series([0])
    
    svpt = pd.concat([w_surf['w_svpt'], l_surf['l_svpt']]).sum() if ('w_svpt' in w_surf.columns and 'l_svpt' in l_surf.columns) else 0
    fst_in = pd.concat([w_surf['w_1stin'], l_surf['l_1stin']]).sum() if ('w_1stin' in w_surf.columns and 'l_1stin' in l_surf.columns) else 0
    fst_won = pd.concat([w_surf['w_1stwon'], l_surf['l_1stwon']]).sum() if ('w_1stwon' in w_surf.columns and 'l_1stwon' in l_surf.columns) else 0
    
    pct_1st_in = (fst_in / svpt * 100) if svpt > 0 else 60.0
    pct_1st_won = (fst_won / fst_in * 100) if fst_in > 0 else 70.0

    avg_games_surf = target_matches['total_games'].dropna().mean()
    
    three_sets_count = 0
    valid_scores_count = 0
    for s_str in target_matches['score']:
        w_s, l_s = parse_sets_count(s_str)
        if not np.isnan(w_s) and (w_s + l_s) >= 2:
            valid_scores_count += 1
            if (w_s + l_s) >= 3:
                three_sets_count += 1

    pct_3_sets = (three_sets_count / valid_scores_count * 100) if valid_scores_count > 0 else 30.0

    return {
        "player_name": player, "overall_winrate": overall_winrate, "recent_form": recent_form,
        "surface_winrate": surface_winrate, "style": player_styles_map.get(player, "Polyvalent"),
        "total_matches": total_m, "avg_tourney_level": avg_tourney_level,
        "last_10_wins": int(recent_form * len(last_10)),
        "avg_aces": aces.mean() * s_config["serve_weight"] if len(aces) > 0 else 0.0,
        "avg_dfs": dfs_count.mean() if len(dfs_count) > 0 else 0.0,
        "pct_1st_in": pct_1st_in, "pct_1st_won": pct_1st_won,
        "avg_games": avg_games_surf if not np.isnan(avg_games_surf) else 22.0,
        "pct_3_sets": pct_3_sets, "pct_tb": 20.0,
        "p_wins": p_wins, "p_losses": p_losses,
        "serve_weight": s_config["serve_weight"], "return_weight": s_config["return_weight"]
    }

stats_a = get_detailed_metrics(player_a, surface)
stats_b = get_detailed_metrics(player_b, surface)

if not stats_a or not stats_b:
    st.warning("Données insuffisantes pour l'un des joueurs.")
    st.stop()

# ---------------------------------------------------------
# 5. MODÈLE DE PROBABILITÉ AVEC PONDÉRATION DE SURFACES SPECIFIQUES
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

# Le calcul réajuste le poids du service/retour selon la sous-surface choisie
serve_adj_a = (stats_a['pct_1st_won'] / 100.0) * stats_a['serve_weight']
serve_adj_b = (stats_b['pct_1st_won'] / 100.0) * stats_b['serve_weight']

rating_a = (
    (stats_a['surface_winrate'] * stats_a['avg_tourney_level'] * 320) + 
    (winrate_a_vs_b_style * 200) + 
    (stats_a['recent_form'] * 150) +
    (serve_adj_a * 100)
)

rating_b = (
    (stats_b['surface_winrate'] * stats_b['avg_tourney_level'] * 320) + 
    (winrate_b_vs_a_style * 200) + 
    (stats_b['recent_form'] * 150) +
    (serve_adj_b * 100)
)

if total_h2h > 0:
    rating_a += (h2h_a_wins - h2h_b_wins) * 30
    rating_b += (h2h_b_wins - h2h_a_wins) * 30

prob_a = 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 500.0))
prob_a = min(max(prob_a, 0.05), 0.95)
prob_b = 1.0 - prob_a

cote_equitable_a, cote_equitable_b = 1 / prob_a, 1 / prob_b

# ---------------------------------------------------------
# 6. CATEGORIE 1 : MATCHUP & PERFORMANCE (ROSE / TITANIUM)
# ---------------------------------------------------------
st.markdown(f"<div class='cat-title-matchup'>📊 Matchup & Performance sur {surface}</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class='player-card-a'>
        <div class='player-header'>
            <div class='player-name-a'>{player_a}</div>
            <div class='style-badge-a'>{stats_a['style']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='card-matchup'>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    g1.metric("Win Global", f"{stats_a['overall_winrate']*100:.0f}%")
    g2.metric("Vs Base", f"{stats_a['surface_winrate']*100:.0f}%")
    g1.metric("Forme", f"{stats_a['last_10_wins']}/10")
    g2.metric("Vs Style", f"{winrate_a_vs_b_style*100:.0f}%")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='player-card-b'>
        <div class='player-header'>
            <div class='player-name-b'>{player_b}</div>
            <div class='style-badge-b'>{stats_b['style']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='card-matchup'>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    g1.metric("Win Global", f"{stats_b['overall_winrate']*100:.0f}%")
    g2.metric("Vs Base", f"{stats_b['surface_winrate']*100:.0f}%")
    g1.metric("Forme", f"{stats_b['last_10_wins']}/10")
    g2.metric("Vs Style", f"{winrate_b_vs_a_style*100:.0f}%")
    st.markdown("</div>", unsafe_allow_html=True)

fav_surface = player_a if stats_a['surface_winrate'] >= stats_b['surface_winrate'] else player_b
fav_style = player_a if winrate_a_vs_b_style >= winrate_b_vs_a_style else player_b

st.markdown(f"""
<div class='analysis-box'>
    💡 <b>Analyse Matchup ({surface}) :</b> Avantage <b>{fav_surface}</b> sur la base de la surface ({max(stats_a['surface_winrate'], stats_b['surface_winrate'])*100:.0f}% V). Profil tactique favorisé : <b>{fav_style}</b> vs le style adverse ({max(winrate_a_vs_b_style, winrate_b_vs_a_style)*100:.0f}% V).
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. CATEGORIE 2 : SERVICE & ENGAGEMENT (BLEU CYAN)
# ---------------------------------------------------------
st.markdown("<div class='cat-title-service'>⚡ Service & Engagement</div>", unsafe_allow_html=True)

s1, s2 = st.columns(2)

with s1:
    st.markdown(f"<span style='color:#fb7185; font-weight:700;'>🎾 {player_a}</span>", unsafe_allow_html=True)
    st.markdown("<div class='card-service'>", unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    p1.metric("Aces / m", f"{stats_a['avg_aces']:.1f}")
    p2.metric("DF / m", f"{stats_a['avg_dfs']:.1f}")
    p1.metric("1st In", f"{stats_a['pct_1st_in']:.0f}%")
    p2.metric("Pts 1st", f"{stats_a['pct_1st_won']:.0f}%")
    st.markdown("</div>", unsafe_allow_html=True)

with s2:
    st.markdown(f"<span style='color:#34d399; font-weight:700;'>🎾 {player_b}</span>", unsafe_allow_html=True)
    st.markdown("<div class='card-service'>", unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    p1.metric("Aces / m", f"{stats_b['avg_aces']:.1f}")
    p2.metric("DF / m", f"{stats_b['avg_dfs']:.1f}")
    p1.metric("1st In", f"{stats_b['pct_1st_in']:.0f}%")
    p2.metric("Pts 1st", f"{stats_b['pct_1st_won']:.0f}%")
    st.markdown("</div>", unsafe_allow_html=True)

fav_serve = player_a if stats_a['pct_1st_won'] >= stats_b['pct_1st_won'] else player_b
st.markdown(f"""
<div class='analysis-box'>
    ⚡ <b>Service sur {surface} :</b> Avantage <b>{fav_serve}</b> ({max(stats_a['pct_1st_won'], stats_b['pct_1st_won']):.0f}% pts 1ère balle).
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. CATEGORIE 3 : FACE-À-FACE DIRECT (VIOLET)
# ---------------------------------------------------------
st.markdown("<div class='cat-title-h2h'>⚔️ Face-à-Face Direct (H2H)</div>", unsafe_allow_html=True)
if total_h2h > 0:
    st.info(f"H2H : **{player_a}** **{h2h_a_wins}** — **{h2h_b_wins}** **{player_b}** ({total_h2h} duels)")
    fav_h2h = player_a if h2h_a_wins > h2h_b_wins else (player_b if h2h_b_wins > h2h_a_wins else "Égalité")
    st.markdown(f"""
    <div class='analysis-box'>
        🤝 <b>H2H :</b> <b>{fav_h2h}</b> mène le bilan direct ({max(h2h_a_wins, h2h_b_wins)} V sur {total_h2h} matchs).
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 Voir la liste des duels"):
        st.dataframe(
            h2h_matches[['tourney_date', 'tourney_name', 'surface', 'round', 'winner_name', 'score']]
            .rename(columns={'tourney_date': 'Date', 'tourney_name': 'Tournoi', 'winner_name': 'Vainqueur', 'round': 'Tour', 'score': 'Score'}),
            use_container_width=True
        )
else:
    st.write("Aucune confrontation directe enregistrée.")

# ---------------------------------------------------------
# 9. CATEGORIE 4 : VALUEBET 1N2 (DORÉ / AMBRE)
# ---------------------------------------------------------
st.markdown("<div class='cat-title-valuebet'>🎯 ValueBet 1N2 (+EV)</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
cote_a = c1.number_input(f"Cote {player_a}", value=float(round(cote_equitable_a, 2)), step=0.05)
cote_b = c2.number_input(f"Cote {player_b}", value=float(round(cote_equitable_b, 2)), step=0.05)

ev_a = (prob_a * cote_a) - 1
ev_b = (prob_b * cote_b) - 1

kelly_a = max(0.0, ((cote_a * prob_a) - 1) / (cote_a - 1)) if cote_a > 1 else 0
kelly_b = max(0.0, ((cote_b * prob_b) - 1) / (cote_b - 1)) if cote_b > 1 else 0

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

# ---------------------------------------------------------
# 10. CATEGORIE 5 : MARCHÉS ANNEXES (ÉMERAUDE)
# ---------------------------------------------------------
st.markdown(f"<div class='cat-title-annexes'>🔥 Marchés Annexes sur {surface}</div>", unsafe_allow_html=True)

combined_avg_games = (stats_a['avg_games'] + stats_b['avg_games']) / 2
combined_3set_pct = (stats_a['pct_3_sets'] + stats_b['pct_3_sets']) / 2
combined_tb_pct = (stats_a['pct_tb'] + stats_b['pct_tb']) / 2

total_projected_aces = stats_a['avg_aces'] + stats_b['avg_aces']
total_projected_dfs = stats_a['avg_dfs'] + stats_b['avg_dfs']

both_big_servers = (stats_a['style'] in ["Gros Serveur", "Serveur-Volleyeur"]) and (stats_b['style'] in ["Gros Serveur", "Serveur-Volleyeur"])
both_returners = (stats_a['style'] in ["Relanceur / Cadenceur", "Contreur / Limeur"]) and (stats_b['style'] in ["Relanceur / Cadenceur", "Contreur / Limeur"])

prob_fav = max(prob_a, prob_b)
fav_player_name = player_a if prob_a > prob_b else player_b
underdog_player_name = player_b if prob_a > prob_b else player_a

is_heavy_blowout = (prob_fav >= 0.78) or (abs(stats_a['quality_score'] - stats_b['quality_score']) >= 0.4)
is_unstable_match = (stats_a['avg_dfs'] >= 4.5 or stats_b['avg_dfs'] >= 4.5) and (combined_3set_pct < 30)

m1_col, m2_col = st.columns(2)

with m1_col:
    with st.container(border=True):
        st.markdown(f"#### 🎾 Over / Under Jeux ({surface})")
        
        j1, j2, j3 = st.columns(3)
        j1.metric("Moy. Jeux", f"{combined_avg_games:.1f}")
        j2.metric("3 Sets", f"{combined_3set_pct:.0f}%")
        j3.metric("Tie-Break", f"{combined_tb_pct:.0f}%")

        if is_heavy_blowout:
            st.error(f"🔴 **PRÉVISION UNDER 20.5 / 21.5 JEUX**\n\n• **Blowout :** **{fav_player_name}** largement favori ({prob_fav*100:.0f}%).")
        elif is_unstable_match:
            st.warning("⚠️ **INCONSTANCE / RISQUE ÉLEVÉ**\n\n• **Breaks fréquents :** Nombreuses DF ({total_projected_dfs:.1f}/m).")
        elif combined_avg_games >= 23.2 or (both_big_servers and combined_avg_games >= 22.0) or combined_3set_pct >= 48:
            st.success("🟢 **RECOMMANDATION : OVER 22.5 JEUX**\n\n• **Match serré :** Fort accrochage pressenti.")
        elif combined_avg_games <= 20.2 or both_returners:
            st.warning("⚡ **RECOMMANDATION : UNDER 21.5 JEUX**\n\n• **Style relanceurs :** Échanges courts et breaks rapides.")
        else:
            st.info("🔵 **MARGE TROP FAIBLE / NO BET**")

    with st.container(border=True):
        st.markdown(f"#### 💥 Over / Under Aces ({surface})")
        
        a1, a2, a3 = st.columns(3)
        a1.metric(f"Aces {player_a[:8]}", f"{stats_a['avg_aces']:.1f}")
        a2.metric(f"Aces {player_b[:8]}", f"{stats_b['avg_aces']:.1f}")
        a3.metric("Total", f"{total_projected_aces:.1f}")

        baseline_aces = 14.5 if surface == "Grass" else (11.5 if surface == "Hard" else 7.5)
        
        if total_projected_aces >= (baseline_aces + 2.5):
            st.success(f"🟢 **RECOMMANDATION : OVER {baseline_aces:.1f} ACES**")
        elif total_projected_aces <= (baseline_aces - 2.5) or surface == "Clay":
            st.error(f"🔴 **RECOMMANDATION : UNDER {baseline_aces:.1f} ACES**")
        else:
            st.info(f"🔵 **MARGE FAIBLE / NO BET** (Projeté : {total_projected_aces:.1f} Aces)")

with m2_col:
    with st.container(border=True):
        st.markdown(f"#### ⚠️ Doubles Fautes ({surface})")
        
        df1, df2, df3 = st.columns(3)
        df1.metric(f"DF {player_a[:8]}", f"{stats_a['avg_dfs']:.1f}")
        df2.metric(f"DF {player_b[:8]}", f"{stats_b['avg_dfs']:.1f}")
        df3.metric("Total", f"{total_projected_dfs:.1f}")

        if total_projected_dfs >= 6.8:
            st.warning("⚡ **RECOMMANDATION : OVER 6.5 DF**")
        elif total_projected_dfs <= 3.8:
            st.success("🟢 **RECOMMANDATION : UNDER 5.5 DF**")
        else:
            st.info("🔵 **MARGE FAIBLE / NO BET**")

    with st.container(border=True):
        st.markdown("#### 🛡️ Handicap Sets")
        
        st.write(f"• **Favori :** `{fav_player_name}` ({prob_fav*100:.0f}%)")
        
        if is_heavy_blowout:
            st.success(f"🚀 **SAFE : {fav_player_name} -1.5 Sets (2-0)**")
        elif combined_3set_pct >= 38 or (0.52 <= prob_fav <= 0.62):
            st.success(f"🛡️ **SAFE : {underdog_player_name} +1.5 Sets**")
        else:
            st.info(f"🔵 **MARGE FAIBLE / Victoire sèche** sur {fav_player_name}")
