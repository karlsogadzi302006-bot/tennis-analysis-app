st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: #0b0f19;
        color: #f1f5f9;
    }
    
    /* En-tête principal */
    .main-title {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #64748b;
        font-size: 0.85rem !important;
        margin-bottom: 16px;
    }

    /* Titres de sections plus grands et lisibles */
    h2, h3, .stHeader {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
        margin-top: 18px !important;
        margin-bottom: 10px !important;
    }

    /* Cartes Joueurs */
    .player-card {
        background: #131a2b;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 10px;
    }
    .player-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .player-name {
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        color: #ffffff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .style-badge {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.72rem !important;
        font-weight: 700;
        text-transform: uppercase;
    }

    /* Métriques ajustées (fini les "..." tronqués) */
    [data-testid="stMetric"] {
        background: #182238 !important;
        border: 1px solid #26334d !important;
        border-radius: 8px !important;
        padding: 8px 6px !important;
        text-align: center !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
        line-height: 1.2 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: #94a3b8 !important;
        white-space: normal !important; /* Autorise le passage à la ligne au lieu de tronquer */
        word-break: break-word !important;
    }

    /* Boîtes d'analyse */
    .analysis-box {
        background: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
        margin-bottom: 16px;
        font-size: 0.88rem !important;
        line-height: 1.4 !important;
        color: #e2e8f0;
    }

    /* Cartes ValueBet */
    .ev-card-success {
        background: rgba(34, 197, 94, 0.08);
        border: 1px solid rgba(34, 197, 94, 0.4);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .ev-card-danger {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
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

df_circuit = load_all_local_atp()

if df_circuit.empty:
    st.error("⚠️ Impossible d'extraire les données des fichiers CSV.")
    st.stop()

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
# 4. CALCULS METRIQUES & STYLES + PONDÉRATION ADAPTÉE
# ---------------------------------------------------------
LEVEL_WEIGHTS = {'G': 1.4, 'M': 1.25, 'A': 1.1, 'C': 0.9, 'S': 0.8, 'D': 0.7}

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

    w_levels = p_wins['tourney_level'].map(LEVEL_WEIGHTS).fillna(1.0) if len(p_wins) > 0 else pd.Series([1.0])
    l_levels = p_losses['tourney_level'].map(LEVEL_WEIGHTS).fillna(1.0) if len(p_losses) > 0 else pd.Series([1.0])
    
    quality_score = (w_levels.sum() * 1.1) / (w_levels.sum() + l_levels.sum()) if (w_levels.sum() + l_levels.sum()) > 0 else 1.0

    overall_winrate = len(p_wins) / total_m
    all_matches = pd.concat([p_wins.assign(is_win=1), p_losses.assign(is_win=0)]).sort_values(by='tourney_date', ascending=False)
    last_10 = all_matches.head(10)
    recent_form = last_10['is_win'].mean() if len(last_10) > 0 else 0.5
    
    surf_wins = p_wins[p_wins['surface'] == surface_match]
    surf_losses = p_losses[p_losses['surface'] == surface_match]
    surf_matches = pd.concat([surf_wins.assign(is_win=1), surf_losses.assign(is_win=0)]).sort_values(by='tourney_date', ascending=False)
    
    total_surf = len(surf_matches)
    surface_winrate = len(surf_wins) / total_surf if total_surf >= 3 else overall_winrate
    
    target_matches = surf_matches.head(12) if total_surf >= 5 else all_matches.head(12)
    
    titles = len(p_wins[p_wins['round'].astype(str).str.upper().isin(['F', 'THE FINAL', 'FINAL'])])
    
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
        "total_surf_matches": total_surf, "quality_score": quality_score,
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
# 5. MODÈLE ELO & MATCHUP TACTIQUE (VS STYLE INCLUS)
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

# RATING GLOBAL : Incorpore fortement la Surface (350 pts) ET le Matchup vs Style (250 pts)
rating_a = (
    (stats_a['surface_winrate'] * 350) + 
    (winrate_a_vs_b_style * 250) + 
    (stats_a['overall_winrate'] * 100) + 
    (stats_a['recent_form'] * 150) + 
    (stats_a['quality_score'] * 150)
)

rating_b = (
    (stats_b['surface_winrate'] * 350) + 
    (winrate_b_vs_a_style * 250) + 
    (stats_b['overall_winrate'] * 100) + 
    (stats_b['recent_form'] * 150) + 
    (stats_b['quality_score'] * 150)
)

# Ajustement selon l'historique H2H
if total_h2h > 0:
    rating_a += (h2h_a_wins - h2h_b_wins) * 30
    rating_b += (h2h_b_wins - h2h_a_wins) * 30

# Calcul de la probabilité logistique (Diviseur 500 pour garder une distribution réaliste)
prob_a = 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 500.0))
prob_a = min(max(prob_a, 0.05), 0.95)
prob_b = 1.0 - prob_a

cote_equitable_a, cote_equitable_b = 1 / prob_a, 1 / prob_b

# ---------------------------------------------------------
# 6. AFFICHAGE : CARTES COMPARATIVES & MATCHUP
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
    
    # Grille 2x2 pour des cases carrées et bien lisibles sur mobile
    g1, g2 = st.columns(2)
    g1.metric("Win Global", f"{stats_a['overall_winrate']*100:.0f}%")
    g2.metric(f"Vs {surface}", f"{stats_a['surface_winrate']*100:.0f}%")
    g1.metric("Forme", f"{stats_a['last_10_wins']}/10")
    g2.metric("Vs Style", f"{winrate_a_vs_b_style*100:.0f}%")

with col2:
    st.markdown(f"""
    <div class='player-card'>
        <div class='player-header'>
            <div class='player-name'>{player_b}</div>
            <div class='style-badge'>{stats_b['style']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Grille 2x2
    g1, g2 = st.columns(2)
    g1.metric("Win Global", f"{stats_b['overall_winrate']*100:.0f}%")
    g2.metric(f"Vs {surface}", f"{stats_b['surface_winrate']*100:.0f}%")
    g1.metric("Forme", f"{stats_b['last_10_wins']}/10")
    g2.metric("Vs Style", f"{winrate_b_vs_a_style*100:.0f}%")

fav_surface = player_a if stats_a['surface_winrate'] >= stats_b['surface_winrate'] else player_b
fav_style = player_a if winrate_a_vs_b_style >= winrate_b_vs_a_style else player_b
st.markdown(f"""
<div class='analysis-box'>
    💡 <b>Surface & Matchup :</b> Avantage <b>{fav_surface}</b> sur {surface} ({max(stats_a['surface_winrate'], stats_b['surface_winrate'])*100:.0f}% V). Meilleur bilan vs le style adverse : <b>{fav_style}</b> ({max(winrate_a_vs_b_style, winrate_b_vs_a_style)*100:.0f}% V).
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. SERVICE & ENGAGEMENT (STRUCTURÉ PAR JOUEUR)
# ---------------------------------------------------------
st.subheader("📊 Service & Engagement")

s1, s2 = st.columns(2)

with s1:
    st.markdown(f"**🎾 {player_a}**")
    p1, p2 = st.columns(2)
    p1.metric("Aces / m", f"{stats_a['avg_aces']:.1f}")
    p2.metric("DF / m", f"{stats_a['avg_dfs']:.1f}")
    p1.metric("1st In", f"{stats_a['pct_1st_in']:.0f}%")
    p2.metric("Pts 1st", f"{stats_a['pct_1st_won']:.0f}%")

with s2:
    st.markdown(f"**🎾 {player_b}**")
    p1, p2 = st.columns(2)
    p1.metric("Aces / m", f"{stats_b['avg_aces']:.1f}")
    p2.metric("DF / m", f"{stats_b['avg_dfs']:.1f}")
    p1.metric("1st In", f"{stats_b['pct_1st_in']:.0f}%")
    p2.metric("Pts 1st", f"{stats_b['pct_1st_won']:.0f}%")

fav_serve = player_a if stats_a['pct_1st_won'] >= stats_b['pct_1st_won'] else player_b
st.markdown(f"""
<div class='analysis-box'>
    ⚡ <b>Service sur {surface} :</b> Avantage <b>{fav_serve}</b> ({max(stats_a['pct_1st_won'], stats_b['pct_1st_won']):.0f}% pts 1ère balle).
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. CONFRONTATIONS DIRECTES (H2H)
# ---------------------------------------------------------
st.subheader("⚔️ Face-à-Face Direct (H2H)")
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
# 9. DETECTEUR +EV ET CALCULATEUR VALUEBET (AVEC SEUIL DE MARGE)
# ---------------------------------------------------------
st.subheader("🎯 ValueBet 1N2 (+EV)")

c1, c2 = st.columns(2)
cote_a = c1.number_input(f"Cote {player_a}", value=float(round(cote_equitable_a, 2)), step=0.05)
cote_b = c2.number_input(f"Cote {player_b}", value=float(round(cote_equitable_b, 2)), step=0.05)

ev_a = (prob_a * cote_a) - 1
ev_b = (prob_b * cote_b) - 1

kelly_a = max(0.0, ((cote_a * prob_a) - 1) / (cote_a - 1)) if cote_a > 1 else 0
kelly_b = max(0.0, ((cote_b * prob_b) - 1) / (cote_b - 1)) if cote_b > 1 else 0

# Seuil minimal d'EV pour valider un ValueBet (2.0%)
EV_MIN_THRESHOLD = 0.02

r1, r2 = st.columns(2)

with r1:
    if ev_a >= EV_MIN_THRESHOLD:
        css_class = "ev-card-success"
    else:
        css_class = "ev-card-danger"
        
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
    if ev_b >= EV_MIN_THRESHOLD:
        css_class = "ev-card-success"
    else:
        css_class = "ev-card-danger"
        
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
# 10. ANALYSE AFFINÉE DES MARCHÉS ANNEXES
# ---------------------------------------------------------
st.subheader(f"🔥 Marchés Annexes sur {surface}")

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
    # 1. OVER / UNDER JEUX
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
            st.info("🔵 **MARGE TROP FAIBLE / NO BET** (Ligne ajustée au marché)")

    # 2. OVER / UNDER ACES
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
    # 3. OVER / UNDER DOUBLES FAUTES
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

   # 4. HANDICAP SETS
    with st.container(border=True):
        st.markdown("#### 🛡️ Handicap Sets")
        
        st.write(f"• **Favori :** `{fav_player_name}` ({prob_fav*100:.0f}%)")
        
        if is_heavy_blowout:
            st.success(f"🚀 **SAFE : {fav_player_name} -1.5 Sets (2-0)**")
        elif combined_3set_pct >= 38 or (0.52 <= prob_fav <= 0.62):
            st.success(f"🛡️ **SAFE : {underdog_player_name} +1.5 Sets**")
        else:
            st.info(f"🔵 **MARGE FAIBLE / Victoire sèche** sur {fav_player_name}")
