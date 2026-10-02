import os
import re
import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import date

# ---------------------------------------------------------
# 1. CONFIGURATION DE PAGE OBLIGATOIRE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tennis ValueBet AI — Analytics ATP",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. DESIGN CSS "CYBER PURPLE NEON & GLASSMORPHISM" COMPLET
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800;900&display=swap');

    /* CONFIGURATION GLOBALE */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #070913 !important;
        color: #f1f5f9 !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1200px !important;
    }

    /* HERO BANNER AVEC GLOW NEON VIOLET CENTRÉ */
    .hero-container {
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 35px 15px 30px 15px !important;
        margin: 0 auto 30px auto !important;
        background: radial-gradient(circle at 50% 30%, rgba(168, 85, 247, 0.25) 0%, rgba(124, 58, 237, 0.08) 45%, rgba(7, 9, 19, 0) 80%) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(168, 85, 247, 0.2) !important;
        box-shadow: 0 0 50px -10px rgba(147, 51, 234, 0.3) !important;
    }

    .main-title {
        font-size: clamp(2.0rem, 6vw, 3.2rem) !important;
        font-weight: 900 !important;
        line-height: 1.15 !important;
        text-align: center !important;
        margin: 0 auto 12px auto !important;
        background: linear-gradient(135deg, #ffffff 10%, #d8b4fe 50%, #c084fc 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        filter: drop-shadow(0 0 18px rgba(192, 132, 252, 0.65)) !important;
        display: block !important;
    }

    .sub-title {
        font-size: clamp(0.85rem, 3vw, 1.05rem) !important;
        color: #cbd5e1 !important;
        text-align: center !important;
        margin: 0 auto !important;
        max-width: 600px !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
        text-shadow: 0 0 10px rgba(168, 85, 247, 0.3);
    }

    /* TITRES DE SECTIONS */
    .cat-title-matchup { color: #f43f5e; font-size: 1.25rem; font-weight: 800; margin-bottom: 12px; filter: drop-shadow(0 0 8px rgba(244, 63, 94, 0.4)); }
    .cat-title-service { color: #38bdf8; font-size: 1.25rem; font-weight: 800; margin-top: 25px; margin-bottom: 12px; filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.4)); }
    .cat-title-h2h { color: #c084fc; font-size: 1.25rem; font-weight: 800; margin-top: 25px; margin-bottom: 12px; filter: drop-shadow(0 0 8px rgba(192, 132, 252, 0.4)); }
    .cat-title-valuebet { color: #fbbf24; font-size: 1.25rem; font-weight: 800; margin-top: 25px; margin-bottom: 12px; filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.4)); }
    .cat-title-annexes { color: #34d399; font-size: 1.25rem; font-weight: 800; margin-top: 25px; margin-bottom: 12px; filter: drop-shadow(0 0 8px rgba(52, 211, 153, 0.4)); }

    /* CARTES DES JOUEURS (EN-TÊTE JOUEUR A ET B) */
    .player-header-a {
        border: 1.5px solid rgba(244, 63, 94, 0.5) !important;
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.12) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .player-header-b {
        border: 1.5px solid rgba(16, 185, 129, 0.5) !important;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .player-name-a { color: #fb7185 !important; font-weight: 800 !important; font-size: 1.2rem !important; }
    .player-name-b { color: #34d399 !important; font-weight: 800 !important; font-size: 1.2rem !important; }

    .style-badge-a {
        background-color: rgba(244, 63, 94, 0.2) !important;
        color: #fda4af !important;
        border: 1px solid rgba(244, 63, 94, 0.4) !important;
        border-radius: 6px !important;
        padding: 3px 10px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }

    .style-badge-b {
        background-color: rgba(16, 185, 129, 0.2) !important;
        color: #a7f3d0 !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 6px !important;
        padding: 3px 10px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }

    /* CARTES MÉTRIQUES & GRILLES */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(20, 27, 45, 0.9) 0%, rgba(13, 17, 30, 0.95) 100%) !important;
        border: 1px solid rgba(168, 85, 247, 0.2) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }

    /* BOX D'ANALYSE */
    .analysis-box {
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.12) 0%, rgba(15, 23, 42, 0.7) 100%) !important;
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        border-left: 4px solid #a855f7 !important;
        padding: 14px 18px !important;
        border-radius: 10px !important;
        margin-top: 15px !important;
        margin-bottom: 15px !important;
        font-size: 0.92rem !important;
    }

    /* VALUEBET TERMINAL CARDS */
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

<!-- HEADER HERO VIOLET NEON -->
<div class='hero-container'>
    <div class='main-title'>🎾 Tennis ValueBet AI Pro</div>
    <div class='sub-title'>Plateforme d'Analyse Prédictive & Détection +EV du Circuit ATP</div>
</div>
""", unsafe_allow_html=True)
# 3. CRÉATION DES ONGLETS (Après la config et le CSS)
tab_tennis, tab_nhl = st.tabs(["🎾 Tennis ValueBet", "🏒 NHL Player Props"])

# 4. CONTENU ONGLET TENNIS
with tab_tennis:
        # Colle ici tout le reste de ton code tennis existant
    
    # ---------------------------------------------------------
    # 3. MATRICE DE STYLES ET FONCTIONS UTILITAIRES
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
    # 4. CHARGEMENT DES DONNÉES SACKMANN (df_circuit)
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
                sub['tourney_level'] = df['tourney_level'].astype(str) if 'tourney_level' in df.columns else "A"
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
    
    # Définition obligatoire de df_circuit
    df_circuit = load_all_local_atp()
    
    if df_circuit.empty:
        st.error("⚠️ Impossible d'extraire les données des fichiers CSV.")
        st.stop()
    
    # ---------------------------------------------------------
    # 5. BARRE DE SÉLECTION DES JOUEURS SUR LA PAGE
    # ---------------------------------------------------------
    SURFACE_VARIATIONS = [
        "Dur rapide", "Dur moyen", "Dur lent", "Dur intérieur / Moquette",
        "Terre battue ocre classique", "Terre battue verte (Har-Tru)", "Terre battue synthétique",
        "Gazon naturel rapide", "Gazon naturel lent (Wimbledon)", "Gazon synthétique"
    ]
    
    SURFACE_FACTORS = {
        "Dur rapide":                     {"serve_weight": 1.30, "return_weight": 0.80, "base_surface": "Hard"},
        "Dur moyen":                      {"serve_weight": 1.00, "return_weight": 1.00, "base_surface": "Hard"},
        "Dur lent":                       {"serve_weight": 0.85, "return_weight": 1.15, "base_surface": "Hard"},
        "Dur intérieur / Moquette":      {"serve_weight": 1.35, "return_weight": 0.75, "base_surface": "Hard"},
        "Terre battue ocre classique":  {"serve_weight": 0.70, "return_weight": 1.30, "base_surface": "Clay"},
        "Terre battue verte (Har-Tru)": {"serve_weight": 0.80, "return_weight": 1.20, "base_surface": "Clay"},
        "Terre battue synthétique":      {"serve_weight": 0.85, "return_weight": 1.15, "base_surface": "Clay"},
        "Gazon naturel rapide":          {"serve_weight": 1.40, "return_weight": 0.70, "base_surface": "Grass"},
        "Gazon naturel lent (Wimbledon)":{"serve_weight": 1.10, "return_weight": 0.95, "base_surface": "Grass"},
        "Gazon synthétique":             {"serve_weight": 1.25, "return_weight": 0.80, "base_surface": "Grass"}
    }
    
    all_players = sorted(list(set(df_circuit['winner_name'].unique()).union(set(df_circuit['loser_name'].unique()))))
    
    # Boîte de sélection principale sur la page
    with st.container():
        st.markdown("### ⚙️ Configuration du Matchup")
        sel_col1, sel_col2, sel_col3 = st.columns([1, 1, 1])
        
        with sel_col1:
            player_a = st.selectbox("🎾 Joueur A", all_players, index=0)
        with sel_col2:
            default_b_idx = 1 if len(all_players) > 1 else 0
            player_b = st.selectbox("🎾 Joueur B", all_players, index=default_b_idx)
        with sel_col3:
            surface = st.selectbox("🌱 Surface spécifique", SURFACE_VARIATIONS)
    
    st.write("") # Espacement
    
    # ---------------------------------------------------------
    # 6. CALCULS METRIQUES & STYLES PONDÉRÉS
    # ---------------------------------------------------------
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
    
    LEVEL_WEIGHTS = {'G': 1.6, 'M': 1.4, 'A': 1.2, 'C': 0.75, 'S': 0.6, 'D': 0.5}
    
    def get_player_matches(df, player_name):
        c_name = clean_name(player_name)
        wins = df[df['winner_clean'] == c_name]
        losses = df[df['loser_clean'] == c_name]
        return wins, losses
    
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
    # 7. CALCUL SELON LES PONDÉRATIONS (35% / 25% / 25% / 15%)
    # ---------------------------------------------------------
    
    # 1. DÉFINITION OBLIGATOIRE DE LA FONCTION AVANT APPEL
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
    
    
    # --- ÉTAPE 1 : SURFACE & CONDITIONS (35% / Coeff 3.5) ---
    serve_adj_a = (stats_a['pct_1st_won'] / 100.0) * stats_a['serve_weight']
    serve_adj_b = (stats_b['pct_1st_won'] / 100.0) * stats_b['serve_weight']
    
    # Intégration du niveau moyen de tournoi (Grand Chelem / M1000 vs ATP 250)
    score_p1_a = (stats_a['surface_winrate'] * 60.0) + (serve_adj_a * 20.0) + ((stats_a['avg_tourney_level'] / 1.6) * 20.0)
    score_p1_b = (stats_b['surface_winrate'] * 60.0) + (serve_adj_b * 20.0) + ((stats_b['avg_tourney_level'] / 1.6) * 20.0)
    
    p1_surface_a = score_p1_a * 3.5
    p1_surface_b = score_p1_b * 3.5
    
    
    # --- ÉTAPE 2 : FORME RÉCENTE & PHYSIQUE (25% / Coeff 2.5) ---
    score_p2_a = stats_a['recent_form'] * 100.0
    score_p2_b = stats_b['recent_form'] * 100.0
    
    p2_forme_a = score_p2_a * 2.5
    p2_forme_b = score_p2_b * 2.5
    
    
    # --- ÉTAPE 3 : MATCH-UP TACTIQUE (25% / Coeff 2.5) ---
    winrate_a_vs_b_style = get_weighted_winrate_vs_style(stats_a, stats_b['style'])
    winrate_b_vs_a_style = get_weighted_winrate_vs_style(stats_b, stats_a['style'])
    
    score_p3_a = winrate_a_vs_b_style * 100.0
    score_p3_b = winrate_b_vs_a_style * 100.0
    
    p3_matchup_a = score_p3_a * 2.5
    p3_matchup_b = score_p3_b * 2.5
    
    
    # --- ÉTAPE 4 : H2H & FACTEUR MENTAL (15% / Coeff 1.5) ---
    clean_a, clean_b = clean_name(player_a), clean_name(player_b)
    h2h_matches = df_circuit[
        ((df_circuit['winner_clean'] == clean_a) & (df_circuit['loser_clean'] == clean_b)) |
        ((df_circuit['winner_clean'] == clean_b) & (df_circuit['loser_clean'] == clean_a))
    ].copy()
    
    s_config = SURFACE_FACTORS.get(surface, {"base_surface": "Hard"})
    base_surf = s_config["base_surface"]
    h2h_surface = h2h_matches[h2h_matches['surface'] == base_surf]
    
    if len(h2h_surface) > 0:
        h2h_a_wins = len(h2h_surface[h2h_surface['winner_clean'] == clean_a])
        h2h_b_wins = len(h2h_surface[h2h_surface['winner_clean'] == clean_b])
        total_h2h = len(h2h_surface)
    else:
        h2h_a_wins = len(h2h_matches[h2h_matches['winner_clean'] == clean_a])
        h2h_b_wins = len(h2h_matches[h2h_matches['winner_clean'] == clean_b])
        total_h2h = len(h2h_matches)
    
    # LISSAGE LAPLACE : Évite les extrêmes (0% ou 100%) sur 1 ou 2 matchs
    score_p4_a = ((h2h_a_wins + 1.0) / (total_h2h + 2.0)) * 100.0
    score_p4_b = ((h2h_b_wins + 1.0) / (total_h2h + 2.0)) * 100.0
    
    p4_mental_a = score_p4_a * 1.5
    p4_mental_b = score_p4_b * 1.5
    
    
    # --- SYNTHÈSE DES RATINGS COMPOSITES ---
    rating_a = p1_surface_a + p2_forme_a + p3_matchup_a + p4_mental_a
    rating_b = p1_surface_b + p2_forme_b + p3_matchup_b + p4_mental_b
    
    
    # --- ÉTAPE 5 : CALCUL DE VALUE (LOGISTIQUE AJUSTÉE) ---
    delta_rating = rating_a - rating_b
    # Facteur d'échelle 420 pour éviter la sur-réaction aux légers deltas
    prob_a = 1.0 / (1.0 + 10.0 ** (-delta_rating / 420.0))
    
    prob_a = min(max(prob_a, 0.05), 0.95)
    prob_b = 1.0 - prob_a
    
    cote_equitable_a = 1.0 / prob_a
    cote_equitable_b = 1.0 / prob_b
    
    # ---------------------------------------------------------
    # 8. AFFICHAGE DES CATEGORIES
    # ---------------------------------------------------------
    st.markdown(f"<div class='cat-title-matchup'>📊 Matchup & Performance sur {surface}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # En-tête Joueur A
        st.markdown(f"""
        <div class='player-header-a'>
            <div class='player-name-a'>{player_a}</div>
            <div class='style-badge-a'>{stats_a['style']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grille de métriques dans un conteneur physique
        with st.container():
            g1, g2 = st.columns(2)
            g1.metric("Win Global", f"{stats_a['overall_winrate']*100:.0f}%")
            g2.metric("Vs Base", f"{stats_a['surface_winrate']*100:.0f}%")
            
            st.write("") # Espacement
            
            g3, g4 = st.columns(2)
            g3.metric("Forme", f"{stats_a['last_10_wins']}/10")
            g4.metric("Vs Style adverse", f"{winrate_a_vs_b_style*100:.0f}%")
    
    with col2:
        # En-tête Joueur B
        st.markdown(f"""
        <div class='player-header-b'>
            <div class='player-name-b'>{player_b}</div>
            <div class='style-badge-b'>{stats_b['style']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grille de métriques dans un conteneur physique
        with st.container():
            g1, g2 = st.columns(2)
            g1.metric("Win Global", f"{stats_b['overall_winrate']*100:.0f}%")
            g2.metric("Vs Base", f"{stats_b['surface_winrate']*100:.0f}%")
            
            st.write("") # Espacement
            
            g3, g4 = st.columns(2)
            g3.metric("Forme", f"{stats_b['last_10_wins']}/10")
            g4.metric("Vs Style adverse", f"{winrate_b_vs_a_style*100:.0f}%")
    
    # Box d'analyse sous les cartes
    fav_surface = player_a if stats_a['surface_winrate'] >= stats_b['surface_winrate'] else player_b
    fav_style = player_a if winrate_a_vs_b_style >= winrate_b_vs_a_style else player_b
    
    st.markdown(f"""
    <div class='analysis-box'>
        💡 <b>Analyse Matchup ({surface}) :</b> Avantage <b>{fav_surface}</b> sur la base de la surface ({max(stats_a['surface_winrate'], stats_b['surface_winrate'])*100:.0f}% V). Profil tactique favorisé : <b>{fav_style}</b> vs le style adverse ({max(winrate_a_vs_b_style, winrate_b_vs_a_style)*100:.0f}% V).
    </div>
    """, unsafe_allow_html=True)
    
    # SERVICE & ENGAGEMENT
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
    
    # H2H
    st.markdown("<div class='cat-title-h2h'>⚔️ Face-à-Face Direct (H2H)</div>", unsafe_allow_html=True)
    if total_h2h > 0:
        st.info(f"H2H : **{player_a}** **{h2h_a_wins}** — **{h2h_b_wins}** **{player_b}** ({total_h2h} duels)")
        fav_h2h = player_a if h2h_a_wins > h2h_b_wins else (player_b if h2h_b_wins > h2h_a_wins else "Égalité")
        st.markdown(f"""
        <div class='analysis-box'>
            🤝 <b>H2H :</b> <b>{fav_h2h}</b> mène le bilan direct ({max(h2h_a_wins, h2h_b_wins)} V sur {total_h2h} matchs).
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write("Aucune confrontation directe enregistrée.")
    
    # VALUEBET 1N2
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
    
    # MARCHÉS ANNEXES
    st.markdown(f"<div class='cat-title-annexes'>🔥 Marchés Annexes sur {surface}</div>", unsafe_allow_html=True)
    
    combined_avg_games = (stats_a['avg_games'] + stats_b['avg_games']) / 2
    combined_3set_pct = (stats_a['pct_3_sets'] + stats_b['pct_3_sets']) / 2
    total_projected_aces = stats_a['avg_aces'] + stats_b['avg_aces']
    total_projected_dfs = stats_a['avg_dfs'] + stats_b['avg_dfs']
    
    prob_fav = max(prob_a, prob_b)
    fav_player_name = player_a if prob_a > prob_b else player_b
    underdog_player_name = player_b if prob_a > prob_b else player_a
    
    m1_col, m2_col = st.columns(2)
    
    with m1_col:
        with st.container(border=True):
            st.markdown(f"#### 🎾 Over / Under Jeux ({surface})")
            
            j1, j2, j3 = st.columns(3)
            j1.metric("Moy. Jeux", f"{combined_avg_games:.1f}")
            j2.metric("3 Sets", f"{combined_3set_pct:.0f}%")
            j3.metric("Tie-Break", f"20%")
    
            if prob_fav >= 0.78:
                st.error(f"🔴 **UNDER 20.5 / 21.5 JEUX**\n\n• **Blowout :** **{fav_player_name}** largement favori ({prob_fav*100:.0f}%).")
            elif combined_avg_games >= 23.2 or combined_3set_pct >= 48:
                st.success("🟢 **OVER 22.5 JEUX**\n\n• **Match serré :** Fort accrochage pressenti.")
            else:
                st.info("🔵 **MARGE TROP FAIBLE / NO BET**")
    
    with m2_col:
        with st.container(border=True):
            st.markdown(f"#### 💥 Over / Under Aces ({surface})")
            
            a1, a2, a3 = st.columns(3)
            a1.metric(f"Aces {player_a[:8]}", f"{stats_a['avg_aces']:.1f}")
            a2.metric(f"Aces {player_b[:8]}", f"{stats_b['avg_aces']:.1f}")
            a3.metric("Total", f"{total_projected_aces:.1f}")
    
            if total_projected_aces >= 12.0:
                st.success("🟢 **RECOMMANDATION : OVER ACES**")
            else:
                st.info(f"🔵 **MARGE FAIBLE / NO BET** (Projeté : {total_projected_aces:.1f} Aces)")
    
    
    





# =========================================================
# 5. CONTENU ONGLET NHL PLAYER PROPS
# =========================================================with tab_nhl:
with tab_nhl:
    st.markdown("<h2 style='text-align:center;color:#a855f7;'>🏒 NHL Player Props Analyzer</h2>",
                unsafe_allow_html=True)
    st.caption("Modèle de Poisson : forme récente + saison, adversaire, PP1, PK et lieu du match")

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    LEAGUE_AVG_GA = 3.05
    STAT_KEY = {"Point": "points", "But": "goals", "Passe": "assists"}

    # ---------- Utilitaires saison ----------
    def current_season_id():
        today = date.today()
        start = today.year if today.month >= 9 else today.year - 1
        return int(f"{start}{start + 1}")

    def previous_season_id(season_id):
        start = int(str(season_id)[:4]) - 1
        return int(f"{start}{start + 1}")

    # ---------- 1. Classement / buts alloués ----------
    @st.cache_data(ttl=3600)
    def fetch_nhl_teams_standings():
        def parse(url):
            res = requests.get(url, headers=HEADERS, timeout=8)
            res.raise_for_status()
            teams = {}
            for t in res.json().get("standings", []):
                gp = t.get("gamesPlayed", 0)
                if gp < 5:
                    return {}
                name = t.get("teamName", {}).get("default", "Inconnu")
                abbrev = t.get("teamAbbrev", {}).get("default", "")
                teams[f"{name} ({abbrev})"] = {
                    "ga_g": round(t.get("goalAgainst", 0) / gp, 2),
                    "abbrev": abbrev,
                }
            return teams

        try:
            teams = parse("[api-web.nhle.com](https://api-web.nhle.com/v1/standings/now)")
            if not teams:
                last_year = int(str(previous_season_id(current_season_id()))[4:])
                teams = parse(f"[api-web.nhle.com](https://api-web.nhle.com/v1/standings/{last_year}-04-15)")
            if teams:
                return dict(sorted(teams.items()))
        except Exception:
            pass
        return {"Adversaire moyen": {"ga_g": LEAGUE_AVG_GA, "abbrev": "AVG"}}

    # ---------- 2. Tous les patineurs ----------
    @st.cache_data(ttl=3600)
    def fetch_skaters_for_season(season_id):
        url = "[api.nhle.com](https://api.nhle.com/stats/rest/en/skater/summary)"
        params = {
            "isAggregate": "false",
            "isGame": "false",
            "start": 0,
            "limit": -1,  # -1 = TOUS les joueurs
            "sort": '[{"property":"points","direction":"DESC"}]',
            "cayenneExp": f"gameTypeId=2 and seasonId={season_id}",
        }
        res = requests.get(url, params=params, headers=HEADERS, timeout=15)
        res.raise_for_status()
        players = []
        for p in res.json().get("data", []):
            name = p.get("skaterFullName")
            if not name:
                continue
            players.append({
                "id": p.get("playerId"),
                "name": f"{name} ({p.get('teamAbbrevs') or 'NHL'})",
                "gamesPlayed": p.get("gamesPlayed") or 0,
                "goals": p.get("goals") or 0,
                "assists": p.get("assists") or 0,
                "points": p.get("points") or 0,
                "shots": p.get("shots") or 0,
                "ppPoints": p.get("ppPoints") or 0,
            })
        return players

    @st.cache_data(ttl=3600)
    def fetch_all_nhl_players():
        season = current_season_id()
        try:
            players = fetch_skaters_for_season(season)
            if len(players) > 300 and max(p["gamesPlayed"] for p in players) >= 5:
                return players, season
        except Exception:
            pass
        prev = previous_season_id(season)
        try:
            return fetch_skaters_for_season(prev), prev
        except Exception:
            return [], prev

    # ---------- 3. Game logs ----------
    @st.cache_data(ttl=1800)
    def fetch_player_game_log(player_id, season_id):
        try:
            url = f"[api-web.nhle.com](https://api-web.nhle.com/v1/player/{player_id}/game-log/{season_id}/2)"
            res = requests.get(url, headers=HEADERS, timeout=8)
            if res.status_code == 200:
                return res.json().get("gameLog", [])
        except Exception:
            pass
        return []

    def filter_logs(logs, period, home_away):
        if home_away == "Domicile":
            logs = [g for g in logs if g.get("homeRoadFlag") == "H"]
        elif home_away == "Extérieur":
            logs = [g for g in logs if g.get("homeRoadFlag") == "R"]
        if period != "Saison":
            logs = logs[: int(period.split()[0])]
        return logs

    # ---------- 4. Modèle ----------
    def expected_rate(player, logs, prop):
        key = STAT_KEY[prop]
        season_rate = player[key] / max(player["gamesPlayed"], 1)
        if not logs:
            return season_rate, season_rate, 0
        n = len(logs)
        recent_rate = sum(g.get(key, 0) for g in logs) / n
        w = n / (n + 15)
        return w * recent_rate + (1 - w) * season_rate, recent_rate, n

    def adjust_lambda(lam, opp_ga, is_pp1, opp_pk, home_away):
        lam *= (opp_ga / LEAGUE_AVG_GA) ** 0.8
        lam *= 1 + max(0.0, (80.0 - opp_pk) / 100) if is_pp1 else 0.92
        if home_away == "Domicile":
            lam *= 1.04
        elif home_away == "Extérieur":
            lam *= 0.97
        return max(lam, 0.001)

    # ---------- 5. Interface ----------
    players_list, season_used = fetch_all_nhl_players()
    teams_dict = fetch_nhl_teams_standings()

    if not players_list:
        st.error("Impossible de charger les joueurs depuis l'API NHL. Réessaie plus tard.")
    else:
        st.caption(f"{len(players_list)} patineurs chargés, saison "
                   f"{str(season_used)[:4]}-{str(season_used)[4:]}")

        min_gp = st.slider("Matchs joués minimum", 0, 40, 5)
        player_dict = {p["name"]: p for p in players_list if p["gamesPlayed"] >= min_gp}

        col1, col2 = st.columns(2)
        with col1:
            label = st.selectbox("Joueur (tape pour chercher)", sorted(player_dict))
            player = player_dict[label]
            period = st.selectbox("Forme récente", ["5 derniers matchs", "10 derniers matchs",
                                                    "20 derniers matchs", "Saison"], index=1)
            prop = st.radio("Pari", ["Point", "But", "Passe"], horizontal=True)
            home_away = st.radio("Lieu", ["Tout", "Domicile", "Extérieur"], horizontal=True)

        with col2:
            st.markdown("### 📊 Adversaire & cote")
            opp = st.selectbox("Équipe adverse", list(teams_dict))
            opp_ga = teams_dict[opp]["ga_g"]
            st.info(f"🛡️ {opp} : **{opp_ga} buts alloués / match**")
            opp_pk = st.slider("PK% adverse", 60.0, 90.0, 79.0, step=0.5)
            is_pp1 = st.checkbox("Joueur sur le PP1",
                                 value=player["ppPoints"] / max(player["gamesPlayed"], 1) > 0.25)
            odds = st.number_input("Cote du bookmaker (décimale)", 1.01, 50.0, 2.00, step=0.05)

        logs = filter_logs(fetch_player_game_log(player["id"], season_used), period, home_away)
        base, recent, n = expected_rate(player, logs, prop)
        lam = adjust_lambda(base, opp_ga, is_pp1, opp_pk, home_away)
        p_model = 1 - math.exp(-lam)
        p_book = 1 / odds
        ev = p_model * odds - 1
        kelly = max(0.0, ev / (odds - 1)) * 0.25

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"{prop}s / match (récent, {n} m.)", f"{recent:.2f}")
        c2.metric("λ ajusté", f"{lam:.2f}")
        c3.metric(f"Proba 1+ {prop}", f"{p_model:.1%}", f"{(p_model - p_book) * 100:+.1f} pts vs cote")
        c4.metric("EV par 1 € misé", f"{ev:+.2f} €")
        st.caption(f"Proba implicite de la cote : {p_book:.1%} · Cote juste selon le modèle : {1 / p_model:.2f}")

        if ev >= 0.08:
            st.success(f"🔥 **Value forte** : {label} 1+ {prop} à {odds}. Mise ≈ {kelly:.1%} de la bankroll.")
        elif ev > 0:
            st.info(f"🟡 **Légère value** : EV {ev:+.1%}. Mise ≈ {kelly:.1%} de la bankroll.")
        else:
            st.error(f"⚠️ **Pas de value** : il faudrait une cote ≥ {1 / p_model:.2f}.")

        if logs:
            with st.expander("Derniers matchs"):
                st.dataframe([{
                    "Date": g.get("gameDate"), "Adv.": g.get("opponentAbbrev"),
                    "Lieu": g.get("homeRoadFlag"), "B": g.get("goals"), "A": g.get("assists"),
                    "Pts": g.get("points"), "Tirs": g.get("shots"), "TOI": g.get("toi"),
                } for g in logs], use_container_width=True)
