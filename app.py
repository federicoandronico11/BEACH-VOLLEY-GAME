import streamlit as st
import database, ui_components, random

st.set_page_config(page_title="Z-SKILLS 26 PRO", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# --- NAVBAR HUB ---
if st.session_state.menu_attivo != "HUB":
    if st.sidebar.button("⬅️ TORNA ALL'HUB"):
        st.session_state.menu_attivo = "HUB"
        st.rerun()

# --- HUB PRINCIPALE ---
if st.session_state.menu_attivo == "HUB":
    st.markdown("<h1 style='text-align: center; color: #00ff85; font-family: Oswald;'>ZERO SKILLS CUP 26</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⚙️ GESTIONE SETUP", use_container_width=True): st.session_state.menu_attivo = "SETUP"; st.rerun()
    with c2:
        if st.button("⚽ MATCH DAY LIVE", use_container_width=True): st.session_state.menu_attivo = "LIVE"; st.rerun()
    with c3:
        if st.button("🏆 CLUB HOUSE", use_container_width=True): st.session_state.menu_attivo = "RANKING"; st.rerun()

# --- SEZIONE SETUP ---
elif st.session_state.menu_attivo == "SETUP":
    st.header("Configurazione Torneo")
    st.session_state.settings['punti_set'] = st.slider("Punti Vittoria Set", 11, 30, 21)
    
    with st.form("iscrizione_fc"):
        c1, c2, c3 = st.columns([2,2,1])
        a1 = c1.selectbox("Atleta 1", [""] + st.session_state.db_atleti)
        a1_n = c1.text_input("Nuovo 1")
        a2 = c2.selectbox("Atleta 2", [""] + st.session_state.db_atleti)
        a2_n = c2.text_input("Nuovo 2")
        quota = c3.number_input("Quota €", 10)
        if st.form_submit_button("REGISTRA TEAM"):
            p1 = a1_n if a1_n else a1
            p2 = a2_n if a2_n else a2
            if p1 and p2:
                st.session_state.teams.append({"name": f"{p1[:3]}-{p2[:3]}".upper(), "p1": p1, "p2": p2, "quota": quota, "pagato": True})
                for p in [p1, p2]:
                    if p not in st.session_state.db_atleti: st.session_state.db_atleti.append(p)
                st.rerun()

    if len(st.session_state.teams) >= 2 and st.button("🚀 GENERA E INIZIA GIRONI"):
        st.session_state.matches = []
        for i in range(len(st.session_state.teams)):
            for j in range(i+1, len(st.session_state.teams)):
                st.session_state.matches.append({"A": st.session_state.teams[i], "B": st.session_state.teams[j], "S1A":0, "S1B":0, "Fatto": False})
        st.session_state.phase = "Gironi"; st.session_state.menu_attivo = "LIVE"; st.rerun()

# --- SEZIONE LIVE (GIRONI + PLAYOFF) ---
elif st.session_state.menu_attivo == "LIVE":
    if st.session_state.phase == "Gironi":
        st.subheader("Fase a Gironi")
        for i, m in enumerate(st.session_state.matches):
            st.markdown(f'<div class="broadcast-card"><div>{m["A"]["name"]}</div><div class="score-box">{m["S1A"]}-{m["S1B"]}</div><div>{m["B"]["name"]}</div></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,1])
            m['S1A'] = c1.number_input("A", 0, 40, m['S1A'], key=f"a{i}")
            m['S1B'] = c2.number_input("B", 0, 40, m['S1B'], key=f"b{i}")
            if c3.button("CONFERMA", key=f"btn{i}"):
                m['Fatto'] = True
                database.aggiorna_carriera(m['A'], m['S1A'], m['S1B'], m['S1A'] > m['S1B'])
                database.aggiorna_carriera(m['B'], m['S1B'], m['S1A'], m['S1B'] > m['S1A'])
                st.rerun()
        
        if all(m['Fatto'] for m in st.session_state.matches) and st.button("🏆 PASSA AI PLAYOFF"):
            # Classifica semplice
            cl = sorted(st.session_state.teams, key=lambda t: sum(1 for m in st.session_state.matches if (m['A']['name']==t['name'] and m['S1A']>m['S1B']) or (m['B']['name']==t['name'] and m['S1B']>m['S1A'])), reverse=True)
            st.session_state.playoffs = [{"A": cl[0], "B": cl[3] if len(cl)>3 else cl[-1], "S1A":0, "S1B":0, "Fatto":False, "N":"Semi 1"},
                                        {"A": cl[1], "B": cl[2] if len(cl)>2 else cl[-1], "S1A":0, "S1B":0, "Fatto":False, "N":"Semi 2"}]
            st.session_state.phase = "Eliminazione"; st.rerun()

    elif st.session_state.phase == "Eliminazione":
        st.subheader("Eliminazione Diretta")
        for i, p in enumerate(st.session_state.playoffs):
            st.markdown(f"**{p['N']}**")
            st.markdown(f'<div class="broadcast-card"><div>{p["A"]["name"]}</div><div class="score-box">{p["S1A"]}-{p["S1B"]}</div><div>{p["B"]["name"]}</div></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,1])
            p['S1A'] = c1.number_input("A", 0, 40, p['S1A'], key=f"p{i}a")
            p['S1B'] = c2.number_input("B", 0, 40, p['S1B'], key=f"p{i}b")
            if c3.button("CONFERMA", key=f"pbtn{i}"):
                p['Fatto'] = True
                database.aggiorna_carriera(p['A'], p['S1A'], p['S1B'], p['S1A'] > p['S1B'])
                database.aggiorna_carriera(p['B'], p['S1B'], p['S1A'], p['S1B'] > p['S1A'])
                st.rerun()
        
        if all(p['Fatto'] for p in st.session_state.playoffs[:2]) and len(st.session_state.playoffs) == 2:
            if st.button("🔥 GENERA FINALE"):
                w1 = st.session_state.playoffs[0]['A'] if st.session_state.playoffs[0]['S1A'] > st.session_state.playoffs[0]['S1B'] else st.session_state.playoffs[0]['B']
                w2 = st.session_state.playoffs[1]['A'] if st.session_state.playoffs[1]['S1A'] > st.session_state.playoffs[1]['S1B'] else st.session_state.playoffs[1]['B']
                st.session_state.playoffs.append({"A": w1, "B": w2, "S1A":0, "S1B":0, "Fatto":False, "N":"FINALISSIMA"})
                st.rerun()
        
        if len(st.session_state.playoffs) > 2:
            f = st.session_state.playoffs[2]
            if f['Fatto']:
                win = f['A'] if f['S1A'] > f['S1B'] else f['B']
                st.balloons()
                st.markdown(f'<div class="winner-reveal"><h1>🏆 CAMPIONI 🏆</h1><h2>{win["name"]}</h2><p>{win["p1"]} & {win["p2"]}</p></div>', unsafe_allow_html=True)
                if st.button("FINISCI E ARCHIVIA"): 
                    st.session_state.phase = "Setup"; st.session_state.teams = []; st.session_state.menu_attivo = "HUB"; st.rerun()

# --- SEZIONE RANKING ---
elif st.session_state.menu_attivo == "RANKING":
    st.title("🏆 CLUB HOUSE")
    rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
    for i, (n, p) in enumerate(rank):
        st.markdown(f"### {i+1}. {n} - {p} PT")
        if n in st.session_state.atleti_stats:
            s = st.session_state.atleti_stats[n]
            st.caption(f"Vinte: {s['v']} | Perse: {s['p']} | Differenziale: {sum(s['history'])}")
