import streamlit as st
import database, ui_components, random, time

st.set_page_config(page_title="Z-SKILLS CUP 26", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# Inizializzazione stato battuta e timer
if 'service_turn' not in st.session_state:
    st.session_state.service_turn = "A"
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- SIDEBAR: LIVE RANKING & CARRIERA ---
with st.sidebar:
    st.markdown("<h2 style='color: #00ff85; font-family: Oswald;'>🏆 LIVE RANKING</h2>", unsafe_allow_html=True)
    if st.session_state.ranking_atleti:
        sorted_rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
        for i, (nome, punti) in enumerate(sorted_rank):
            with st.expander(f"{i+1}. {nome.upper()} - {punti} PT"):
                s = st.session_state.atleti_stats.get(nome, {})
                if s:
                    qp = round(s.get('pf', 0) / max(1, s.get('ps', 1)), 3)
                    qs = round(s.get('sv', 0) / max(1, s.get('sp', 1)), 2)
                    st.markdown(f"🏅 **MEDAGLIE:** {'🥇' * s.get('medaglie', 0)}")
                    c1, c2 = st.columns(2); c1.metric("SET V/P", f"{s.get('sv',0)}/{s.get('sp',0)}"); c2.metric("Q. SET", qs)
                    st.line_chart(s.get('history', []), height=100)
    
    st.divider()
    if st.button("🏠 TORNA ALL'HUB"): 
        st.session_state.menu_attivo = "HUB"
        st.rerun()

# --- HUB PRINCIPALE ---
if st.session_state.menu_attivo == "HUB":
    st.markdown("<h1 style='text-align: center; color: #00ff85; font-family: Oswald; letter-spacing: 4px;'>ZERO SKILLS CUP 26</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="fc-tile"><h2>GESTIONE</h2><p>Iscrizioni & Setup</p></div>', unsafe_allow_html=True)
        if st.button("SETUP TORNEO", use_container_width=True): 
            st.session_state.menu_attivo = "SETUP"
            st.rerun()
    with c2:
        st.markdown('<div class="fc-tile"><h2>MATCH DAY</h2><p>Risultati Live</p></div>', unsafe_allow_html=True)
        if st.button("CAMPO LIVE", use_container_width=True): 
            st.session_state.menu_attivo = "LIVE"
            st.rerun()
    with c3:
        st.markdown('<div class="fc-tile"><h2>CLUB HOUSE</h2><p>Hall of Fame</p></div>', unsafe_allow_html=True)
        if st.button("RANKING TOTALE", use_container_width=True): 
            st.session_state.menu_attivo = "RANKING"
            st.rerun()

# --- SEZIONE SETUP ---
elif st.session_state.menu_attivo == "SETUP":
    st.markdown("<h2 style='color: #00ff85; font-family: Oswald;'>⚙️ CONFIGURAZIONE TORNEO</h2>", unsafe_allow_html=True)
    col_cfg, col_pay = st.columns([2,1])
    with col_cfg:
        st.session_state.settings['match_type'] = st.radio("FORMATO MATCH", ["Set Unico", "Best of 3"], horizontal=True)
        st.session_state.settings['punti_set'] = st.slider("PUNTI VITTORIA SET", 11, 30, st.session_state.settings['punti_set'])
    
    with st.form("iscrizione_squadre_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        at1 = c1.text_input("Atleta 1")
        at2 = c2.text_input("Atleta 2")
        if st.form_submit_button("REGISTRA SQUADRA"):
            if at1 and at2:
                new_team = {"name": f"{at1[:3]}-{at2[:3]}".upper(), "p1": at1, "p2": at2, "quota": 10, "pagato": True, "is_bye": False}
                st.session_state.teams.append(new_team)
                st.rerun()

    if len(st.session_state.teams) >= 2:
        if st.button("🚀 GENERA TABELLONE", type="primary", use_container_width=True):
            st.session_state.matches = []
            for i in range(0, len(st.session_state.teams), 2):
                if i+1 < len(st.session_state.teams):
                    st.session_state.matches.append({"A": st.session_state.teams[i], "B": st.session_state.teams[i+1], "S1A": 0, "S1B": 0, "Fatto": False})
            st.session_state.phase = "Gironi"
            st.session_state.menu_attivo = "LIVE"
            st.rerun()

# --- SEZIONE LIVE (IL TUO TABELLONE) ---
elif st.session_state.menu_attivo == "LIVE":
    st.markdown("<h2 style='color: #00ff85; font-family: Oswald;'>🎮 SCOREBOARD LIVE</h2>", unsafe_allow_html=True)
    match_corrente = next((m for m in st.session_state.matches if not m['Fatto']), None)

    if match_corrente:
        # Timer Management
        if st.session_state.start_time is None:
            if st.button("⏱️ AVVIA MATCH", use_container_width=True):
                st.session_state.start_time = time.time()
                st.rerun()
            elapsed = "00:00"
        else:
            diff = int(time.time() - st.session_state.start_time)
            elapsed = f"{diff // 60:02d}:{diff % 60:02d}"

        st.markdown(f"<div class='timer-box-live'>LIVE CLOCK: {elapsed}</div>", unsafe_allow_html=True)

        # Tabellone Grafico
        st.markdown("<div class='main-container-sb'>", unsafe_allow_html=True)
        col1, col_mid, col2 = st.columns([2, 0.5, 2])
        
        with col1:
            serv_a = "<span class='ball-icon-live'>🏐</span>" if st.session_state.service_turn == 'A' else ""
            st.markdown(f"<div class='team-red-bg'><h3>{match_corrente['A']['name']}</h3><div class='score-val-big'>{match_corrente['S1A']}</div><div style='height:40px'>{serv_a}</div></div>", unsafe_allow_html=True)
            if st.button("➕ PT RED", key="add_a"): 
                match_corrente['S1A'] += 1
                st.session_state.service_turn = "A"
                st.rerun()

        with col_mid:
            st.markdown("<h1 style='text-align: center; margin-top: 50px;'>VS</h1>", unsafe_allow_html=True)
            if st.button("🔃"):
                st.session_state.service_turn = "B" if st.session_state.service_turn == "A" else "A"
                st.rerun()

        with col2:
            serv_b = "<span class='ball-icon-live'>🏐</span>" if st.session_state.service_turn == 'B' else ""
            st.markdown(f"<div class='team-blue-bg'><h3>{match_corrente['B']['name']}</h3><div class='score-val-big'>{match_corrente['S1B']}</div><div style='height:40px'>{serv_b}</div></div>", unsafe_allow_html=True)
            if st.button("➕ PT BLUE", key="add_b"): 
                match_corrente['S1B'] += 1
                st.session_state.service_turn = "B"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🚀 SALVA RISULTATO FINALE", type="primary", use_container_width=True):
            # --- FIX ANTI-CRASH (Inizializzazione forzata chiavi mancanti) ---
            for player_name in [match_corrente['A']['p1'], match_corrente['A']['p2'], match_corrente['B']['p1'], match_corrente['B']['p2']]:
                if player_name not in st.session_state.atleti_stats:
                    st.session_state.atleti_stats[player_name] = {}
                
                # Assicuriamoci che tutte le chiavi richieste da database.py esistano
                defaults = {'p': 0, 'sv': 0, 'sp': 0, 'pf': 0, 'ps': 0, 'medaglie': 0, 'history': [], 'match_logs': []}
                for key, val in defaults.items():
                    if key not in st.session_state.atleti_stats[player_name]:
                        st.session_state.atleti_stats[player_name][key] = val
            
            # Chiamata al database (Ora sicura)
            database.aggiorna_carriera(match_corrente['A'], match_corrente['S1A'], match_corrente['S1B'], match_corrente['S1A'] > match_corrente['S1B'], 1 if match_corrente['S1A']>match_corrente['S1B'] else 0, 1 if match_corrente['S1B']>match_corrente['S1A'] else 0)
            database.aggiorna_carriera(match_corrente['B'], match_corrente['S1B'], match_corrente['S1A'], match_corrente['S1B'] > match_corrente['S1A'], 1 if match_corrente['S1B']>match_corrente['S1A'] else 0, 1 if match_corrente['S1A']>match_corrente['S1B'] else 0)
            
            match_corrente['Fatto'] = True
            st.session_state.start_time = None
            st.success("Match Salvato!")
            st.rerun()
    else:
        st.success("Tutti i match completati!")

# --- RANKING ---
elif st.session_state.menu_attivo == "RANKING":
    st.markdown("<h1 style='text-align: center; color: #00ff85; font-family: Oswald;'>🏆 HALL OF FAME</h1>", unsafe_allow_html=True)
    rank_list = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
    for i, (n, p) in enumerate(rank_list):
        st.write(f"**{i+1}º {n}** - {p} PT")
