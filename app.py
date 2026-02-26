import streamlit as st
import database, ui_components, random

st.set_page_config(page_title="Z-SKILLS CUP 26", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# --- HUB PRINCIPALE ---
if st.session_state.menu_attivo == "HUB":
    st.markdown("<h1 style='text-align: center; color: #00ff85; font-family: Oswald; letter-spacing: 5px;'>ZERO SKILLS CUP 26</h1>", unsafe_allow_html=True)
    st.write("---")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="fc-tile"><h2>GESTIONE</h2><p>Setup Torneo e Iscrizioni</p></div>', unsafe_allow_html=True)
        if st.button("CONFIGURA EVENTO"): st.session_state.menu_attivo = "SETUP"; st.rerun()
    with c2:
        st.markdown('<div class="fc-tile"><h2>MATCH DAY</h2><p>Scoreboard Live e Risultati</p></div>', unsafe_allow_html=True)
        if st.button("VAI AL CAMPO"): st.session_state.menu_attivo = "LIVE"; st.rerun()
    with c3:
        st.markdown('<div class="fc-tile"><h2>RANKING</h2><p>Club House & Carriera</p></div>', unsafe_allow_html=True)
        if st.button("VEDI CLASSIFICA"): st.session_state.menu_attivo = "RANKING"; st.rerun()

# --- SEZIONE SETUP ---
elif st.session_state.menu_attivo == "SETUP":
    st.markdown("### ⚙️ IMPOSTAZIONI TORNEO")
    
    with st.container():
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.session_state.settings['formato'] = st.radio("TIPOLOGIA TABELLONE", ["Gironi + Eliminazione", "Doppia Eliminazione"])
            st.session_state.settings['match_type'] = st.radio("FORMATO PARTITA", ["Set Unico", "Best of 3"])
            st.session_state.settings['richiesta_nome'] = st.toggle("Richiedi Nome Squadra Custom", value=False)
        with col_s2:
            st.session_state.settings['punti_set'] = st.slider("PUNTEGGIO MASSIMO SET", 11, 30, 21)
            incasso = sum(t['quota'] for t in st.session_state.teams if t['pagato'])
            st.metric("INCASSO LIVE", f"{incasso} €", delta=f"{len(st.session_state.teams)} Team")

    st.write("---")
    st.subheader("📝 ISCRIZIONE SQUADRA")
    with st.form("iscrizione_pro", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        # Logica Tendina + Nuovo Atleta
        at1 = c1.selectbox("Atleta 1 (Esistente)", [""] + st.session_state.db_atleti)
        at1_n = c1.text_input("...oppure Nuovo Atleta 1")
        at2 = c2.selectbox("Atleta 2 (Esistente)", [""] + st.session_state.db_atleti)
        at2_n = c2.text_input("...oppure Nuovo Atleta 2")
        
        custom_name = ""
        if st.session_state.settings['richiesta_nome']:
            custom_name = st.text_input("Nome Squadra Custom")
        
        quota_on = c3.toggle("Quota Pagata", value=True)
        quota_val = c3.number_input("Quota €", 0, 100, 10)
        
        if st.form_submit_button("REGISTRA TEAM"):
            p1 = at1_n if at1_n else at1
            p2 = at2_n if at2_n else at2
            if p1 and p2:
                t_name = custom_name if custom_name else f"{p1[:3]}-{p2[:3]}".upper()
                st.session_state.teams.append({"name": t_name, "p1": p1, "p2": p2, "quota": quota_val, "pagato": quota_on})
                for p in [p1, p2]:
                    if p not in st.session_state.db_atleti: st.session_state.db_atleti.append(p)
                st.rerun()

    if len(st.session_state.teams) >= 2:
        if st.button("🚀 GENERA TORNEO E INIZIA", type="primary", use_container_width=True):
            # Generazione calendario (Gironi semplificati)
            st.session_state.matches = []
            for i in range(len(st.session_state.teams)):
                for j in range(i+1, len(st.session_state.teams)):
                    st.session_state.matches.append({
                        "A": st.session_state.teams[i], "B": st.session_state.teams[j],
                        "S1A":0, "S1B":0, "Fatto": False
                    })
            st.session_state.phase = "Gironi"
            st.session_state.menu_attivo = "LIVE"
            st.rerun()
            
    if st.button("⬅️ HUB"): st.session_state.menu_attivo = "HUB"; st.rerun()

# --- SEZIONE LIVE (DAZN / FC 26 STYLE) ---
elif st.session_state.menu_attivo == "LIVE":
    st.markdown("<h2 style='color: #00ff85;'>📺 MATCH DAY LIVE</h2>", unsafe_allow_html=True)
    
    if not st.session_state.matches:
        st.warning("Nessun match generato. Vai nel Setup.")
    else:
        # Simulatore Rapido
        if st.button("🎲 SIMULA RISULTATI MANCANTI"):
            limit = st.session_state.settings['punti_set']
            for m in st.session_state.matches:
                if not m['Fatto']:
                    m['S1A'] = random.randint(limit-5, limit+2); m['S1B'] = limit if m['S1A'] < limit else m['S1A']-2
                    m['Fatto'] = True
            st.rerun()

        for i, m in enumerate(st.session_state.matches):
            st.markdown(f"""
            <div class="broadcast-card">
                <div class="team-red">{m['A']['name']}</div>
                <div class="score-box">{m['S1A']} - {m['S1B']}</div>
                <div class="team-blue">{m['B']['name']}</div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,2])
            m['S1A'] = c1.number_input("Punti A", 0, 45, m['S1A'], key=f"s1a{i}")
            m['S1B'] = c2.number_input("Punti B", 0, 45, m['S1B'], key=f"s1b{i}")
            m['Fatto'] = c3.checkbox("CONFERMA RISULTATO", m['Fatto'], key=f"f{i}")
            st.divider()

    if st.button("⬅️ HUB"): st.session_state.menu_attivo = "HUB"; st.rerun()

# --- SEZIONE RANKING ---
elif st.session_state.menu_attivo == "RANKING":
    st.title("🏆 RANKING GENERALE")
    # Qui andrà la logica del podio e carriera descritta precedentemente
    st.info("Visualizzazione Carriera Atleti in arrivo...")
    if st.button("⬅️ HUB"): st.session_state.menu_attivo = "HUB"; st.rerun()
