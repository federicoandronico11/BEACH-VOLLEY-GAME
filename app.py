import streamlit as st
import database, ui_components, random

st.set_page_config(page_title="Z-SKILLS CUP 26", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# --- SIDEBAR: LIVE RANKING & CARRIERA ---
with st.sidebar:
    st.markdown("<h2 style='color: #00ff85; font-family: Oswald;'>🏆 LIVE RANKING</h2>", unsafe_allow_html=True)
    if st.session_state.ranking_atleti:
        sorted_rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
        for i, (nome, punti) in enumerate(sorted_rank):
            with st.expander(f"{i+1}. {nome.upper()} - {punti} PT"):
                s = st.session_state.atleti_stats.get(nome, {})
                if s:
                    qp = round(s['pf'] / max(1, s['ps']), 3)
                    qs = round(s['sv'] / max(1, s['sp']), 2)
                    st.markdown(f"🏅 **MEDAGLIE:** {'🥇' * s['medaglie']}")
                    c1, c2 = st.columns(2); c1.metric("SET V/P", f"{s['sv']}/{s['sp']}"); c2.metric("Q. SET", qs)
                    c3, c4 = st.columns(2); c3.metric("PUNTI F/S", f"{s['pf']}/{s['ps']}"); c4.metric("Q. PUNTI", qp)
                    st.line_chart(s['history'], height=100)
    else: st.info("Inizia un match per vedere il ranking")
    st.divider()
    if st.button("🏠 TORNA ALL'HUB"): st.session_state.menu_attivo = "HUB"; st.rerun()

# --- HUB PRINCIPALE ---
if st.session_state.menu_attivo == "HUB":
    st.markdown("<h1 style='text-align: center; color: #00ff85; font-family: Oswald; letter-spacing: 4px;'>ZERO SKILLS CUP 26</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="fc-tile"><h2>GESTIONE</h2><p>Iscrizioni & Setup</p></div>', unsafe_allow_html=True)
        if st.button("SETUP TORNEO", use_container_width=True): st.session_state.menu_attivo = "SETUP"; st.rerun()
    with c2:
        st.markdown('<div class="fc-tile"><h2>MATCH DAY</h2><p>Risultati Live</p></div>', unsafe_allow_html=True)
        if st.button("CAMPO LIVE", use_container_width=True): st.session_state.menu_attivo = "LIVE"; st.rerun()
    with c3:
        st.markdown('<div class="fc-tile"><h2>CLUB HOUSE</h2><p>Hall of Fame</p></div>', unsafe_allow_html=True)
        if st.button("RANKING TOTALE", use_container_width=True): st.session_state.menu_attivo = "RANKING"; st.rerun()

# --- SEZIONE SETUP ---
elif st.session_state.menu_attivo == "SETUP":
    st.header("⚙️ Configurazione")
    col_cfg, col_pay = st.columns([2,1])
    with col_cfg:
        st.session_state.settings['match_type'] = st.radio("Formato Match", ["Set Unico", "Best of 3"], horizontal=True)
        st.session_state.settings['punti_set'] = st.slider("Punti Set", 11, 30, 21)
    with col_pay:
        incasso = sum(t['quota'] for t in st.session_state.teams if t['pagato'])
        st.metric("INCASSO TOTALE", f"{incasso}€", f"{len(st.session_state.teams)} Team")

    st.divider()
    with st.form("iscrizione_pro", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        at1 = c1.selectbox("Atleta 1", [""] + st.session_state.db_atleti); at1_new = c1.text_input("...o Nuovo Nome")
        at2 = c2.selectbox("Atleta 2", [""] + st.session_state.db_atleti); at2_new = c2.text_input("...o Nuovo Nome")
        q_val = c3.number_input("Quota €", 10); q_on = c3.toggle("Pagato", value=True)
        if st.form_submit_button("REGISTRA SQUADRA"):
            p1 = at1_new if at1_new else at1; p2 = at2_new if at2_new else at2
            if p1 and p2:
                st.session_state.teams.append({"name": f"{p1[:3]}-{p2[:3]}".upper(), "p1": p1, "p2": p2, "quota": q_val, "pagato": q_on})
                if p1 not in st.session_state.db_atleti: st.session_state.db_atleti.append(p1)
                if p2 not in st.session_state.db_atleti: st.session_state.db_atleti.append(p2)
                st.rerun()
    
    if len(st.session_state.teams) >= 2 and st.button("🚀 GENERA TABELLONE", type="primary", use_container_width=True):
        st.session_state.matches = []
        for i in range(len(st.session_state.teams)):
            for j in range(i+1, len(st.session_state.teams)):
                st.session_state.matches.append({"A": st.session_state.teams[i], "B": st.session_state.teams[j], "S1A":0, "S1B":0, "Fatto": False})
        st.session_state.phase = "Gironi"; st.session_state.menu_attivo = "LIVE"; st.rerun()

# --- SEZIONE LIVE ---
elif st.session_state.menu_attivo == "LIVE":
    if st.session_state.phase == "Gironi":
        st.subheader("📺 Fase a Gironi")
        for i, m in enumerate(st.session_state.matches):
            st.markdown(f'<div class="broadcast-card"><div class="team-red">{m["A"]["name"]}</div><div class="score-box">{m["S1A"]}-{m["S1B"]}</div><div class="team-blue">{m["B"]["name"]}</div></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,1])
            m['S1A'] = c1.number_input("Punti A", 0, 45, m['S1A'], key=f"s1a{i}")
            m['S1B'] = c2.number_input("Punti B", 0, 45, m['S1B'], key=f"s1b{i}")
            if c3.button("CONFERMA", key=f"btn{i}"):
                m['Fatto'] = True
                database.aggiorna_carriera(m['A'], m['S1A'], m['S1B'], m['S1A'] > m['S1B'], 1 if m['S1A']>m['S1B'] else 0, 1 if m['S1B']>m['S1A'] else 0)
                database.aggiorna_carriera(m['B'], m['S1B'], m['S1A'], m['S1B'] > m['S1A'], 1 if m['S1B']>m['S1A'] else 0, 1 if m['S1A']>m['S1B'] else 0)
                st.rerun()
        
        if all(m['Fatto'] for m in st.session_state.matches) and st.button("🏆 PASSA AI PLAYOFF"):
            cl = sorted(st.session_state.teams, key=lambda t: sum(1 for m in st.session_state.matches if (m['A']['name']==t['name'] and m['S1A']>m['S1B'])), reverse=True)
            st.session_state.playoffs = [{"A": cl[0], "B": cl[3] if len(cl)>3 else cl[-1], "S1A":0, "S1B":0, "Fatto":False, "N":"Semi 1"},
                                        {"A": cl[1], "B": cl[2] if len(cl)>2 else cl[-1], "S1A":0, "S1B":0, "Fatto":False, "N":"Semi 2"}]
            st.session_state.phase = "Eliminazione"; st.rerun()

    elif st.session_state.phase == "Eliminazione":
        st.subheader("🔥 Fase Finale")
        for i, p in enumerate(st.session_state.playoffs):
            st.markdown(f"**{p['N']}**")
            st.markdown(f'<div class="broadcast-card"><div>{p["A"]["name"]}</div><div class="score-box">{p["S1A"]}-{p["S1B"]}</div><div>{p["B"]["name"]}</div></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,1])
            p['S1A'] = c1.number_input("Punti A", 0, 45, p['S1A'], key=f"pa{i}"); p['S1B'] = c2.number_input("Punti B", 0, 45, p['S1B'], key=f"pb{i}")
            if c3.button("CONFERMA", key=f"pbtn{i}"):
                p['Fatto'] = True
                database.aggiorna_carriera(p['A'], p['S1A'], p['S1B'], p['S1A'] > p['S1B'], 1 if p['S1A']>p['S1B'] else 0, 1 if p['S1B']>p['S1A'] else 0)
                database.aggiorna_carriera(p['B'], p['S1B'], p['S1A'], p['S1B'] > p['S1A'], 1 if p['S1B']>p['S1A'] else 0, 1 if p['S1A']>p['S1B'] else 0)
                st.rerun()
        
        if all(p['Fatto'] for p in st.session_state.playoffs[:2]) and len(st.session_state.playoffs) == 2:
            if st.button("🏁 GENERA FINALISSIMA"):
                w1 = st.session_state.playoffs[0]['A'] if st.session_state.playoffs[0]['S1A'] > st.session_state.playoffs[0]['S1B'] else st.session_state.playoffs[0]['B']
                w2 = st.session_state.playoffs[1]['A'] if st.session_state.playoffs[1]['S1A'] > st.session_state.playoffs[1]['S1B'] else st.session_state.playoffs[1]['B']
                st.session_state.playoffs.append({"A": w1, "B": w2, "S1A":0, "S1B":0, "Fatto":False, "N":"FINALISSIMA"}); st.rerun()
        
        if len(st.session_state.playoffs) > 2:
            f = st.session_state.playoffs[2]
            if f['Fatto']:
                win = f['A'] if f['S1A'] > f['S1B'] else f['B']
                st.balloons()
                st.markdown(f'<div class="winner-reveal"><h1>🏆 CAMPIONI 🏆</h1><h2>{win["name"]}</h2><p>{win["p1"]} & {win["p2"]}</p></div>', unsafe_allow_html=True)
                if st.button("💾 ARCHIVIA E CHIUDI TORNEO"):
                    for a in [win['p1'], win['p2']]:
                        if a in st.session_state.atleti_stats: st.session_state.atleti_stats[a]['medaglie'] += 1
                    st.session_state.phase = "Setup"; st.session_state.teams = []; st.session_state.menu_attivo = "HUB"; st.rerun()

# --- SEZIONE RANKING ---
elif st.session_state.menu_attivo == "RANKING":
    st.title("🏆 HALL OF FAME")
    # Qui la logica del ranking è duplicata dalla sidebar per chi vuole vederla a tutto schermo
    rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
    for i, (n, p) in enumerate(rank):
        st.markdown(f"### {i+1}. {n.upper()} - {p} PT")
