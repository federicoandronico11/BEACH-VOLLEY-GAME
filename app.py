import streamlit as st
import pandas as pd
import database, ui_components, ranking_page, simulator, scoreboard

st.set_page_config(page_title="Z-Skills Pro Tournament", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# SIDEBAR AVANZATA
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/732/732244.png", width=80)
    st.title("PRO DASHBOARD")
    nav = st.selectbox("MENU PRINCIPALE", ["⚙️ SETUP TORNEO", "📺 TABELLONE LIVE", "🏆 RANKING & CARRIERA"])
    st.divider()
    
    st.subheader("📊 TOP 5 LIVE")
    top_5 = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (n, p) in enumerate(top_5):
        st.caption(f"{i+1}. {n} | {p} PT")

# 1. SETUP TORNEO
if nav == "⚙️ SETUP TORNEO":
    st.header("Impostazioni Evento")
    
    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
        st.session_state.settings['formato'] = st.selectbox("Tabellone", ["Gironi + Eliminazione", "Doppia Eliminazione"])
        st.session_state.match_type = st.radio("Serie", ["Set Unico", "Best of 3"])
    with col_cfg2:
        st.session_state.settings['punti_set'] = st.number_input("Punti Set", 10, 31, 21)
        st.session_state.nome_squadra_auto = st.toggle("Nomi Auto (TRIP-LET)", value=True)
    with col_cfg3:
        incasso_data = database.esporta_incassi_csv()
        if incasso_data:
            st.download_button("📥 Esporta Storico Incassi", incasso_data, "storico_tornei.csv", "text/csv")
        st.metric("SQUADRE ISCRITTE", len(st.session_state.teams))

    st.write("---")
    
    # ISCRIZIONE CON AUTO-SUGGEST
    with st.container():
        st.subheader("📝 Iscrizione Team")
        c1, c2, c3 = st.columns([2,2,1])
        with c1:
            at1 = st.text_input("Atleta 1 (Nuovo)", key="at1_n")
            at1_ex = st.selectbox("Seleziona Esistente 1", [""] + st.session_state.db_atleti)
        with c2:
            at2 = st.text_input("Atleta 2 (Nuovo)", key="at2_n")
            at2_ex = st.selectbox("Seleziona Esistente 2", [""] + st.session_state.db_atleti)
        with c3:
            quota = st.number_input("Quota €", 10)
            pagato = st.checkbox("Versato")
        
        if st.button("➕ AGGIUNGI TEAM", use_container_width=True):
            p1 = at1 if at1 else at1_ex
            p2 = at2 if at2 else at2_ex
            if p1 and p2:
                name = f"{p1[:3]}-{p2[:3]}".upper() if st.session_state.nome_squadra_auto else f"Team {len(st.session_state.teams)+1}"
                st.session_state.teams.append({"name": name, "p1": p1, "p2": p2, "quota": quota, "pagato": pagato})
                for p in [p1, p2]:
                    if p not in st.session_state.db_atleti: st.session_state.db_atleti.append(p)
                st.rerun()

    if len(st.session_state.teams) >= 2:
        if st.button("🚀 GENERA TABELLONE E INIZIA", type="primary", use_container_width=True):
            st.session_state.matches = simulator.create_calendar(st.session_state.teams)
            st.session_state.phase = "Gironi"
            st.rerun()

# 2. TABELLONE LIVE (STILE DAZN)
elif nav == "📺 TABELLONE LIVE":
    st.header("Punteggi in Diretta")
    
    with st.expander("🛠️ DEVELOPER SIMULATOR", expanded=False):
        st.session_state.sim_to_rank = st.toggle("Invia dati simulazione a Ranking/Hall of Fame")
        if st.button("🎲 SIMULA TUTTI I RISULTATI"):
            simulator.run_full_sim()
            st.rerun()

    # Visualizzazione Match
    for i, m in enumerate(st.session_state.matches):
        with st.container():
            st.markdown(f"""
            <div class="dazn-match-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="team-red">🔴 {m['A']['name']}</div>
                    <div class="score-badge">{m.get('S1A',0)} - {m.get('S1B',0)}</div>
                    <div class="team-blue">🔵 {m['B']['name']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([1,1,1,1])
            m['S1A'] = c1.number_input(f"S1 A", 0, 45, m.get('S1A',0), key=f"s1a{i}")
            m['S1B'] = c2.number_input(f"S1 B", 0, 45, m.get('S1B',0), key=f"s1b{i}")
            if st.session_state.match_type == "Best of 3":
                m['S2A'] = c3.number_input(f"S2 A", 0, 45, m.get('S2A',0), key=f"s2a{i}")
                m['S2B'] = c4.number_input(f"S2 B", 0, 45, m.get('S2B',0), key=f"s2b{i}")
            
            m['Fatto'] = st.checkbox("CONFERMA RISULTATO", m.get('Fatto', False), key=f"f{i}")
            st.write("---")

# 3. RANKING & CARRIERA
elif nav == "🏆 RANKING & CARRIERA":
    ranking_page.render_all()
