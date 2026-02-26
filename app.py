import streamlit as st
import database, ui_components, simulator, ranking_page

st.set_page_config(page_title="Z-Skills Pro", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

with st.sidebar:
    st.title("🎮 CONTROLLO")
    nav = st.radio("Navigazione", ["Setup", "Live", "Ranking"])
    st.divider()
    if st.button("🗑️ Reset Torneo"):
        st.session_state.phase = "Setup"; st.session_state.teams = []; st.session_state.matches = []; st.rerun()

if nav == "Setup":
    st.header("⚙️ Configurazione")
    c1, c2 = st.columns(2)
    st.session_state.settings['punti_set'] = c1.number_input("Punti Set", 10, 30, 21)
    st.session_state.match_type = c2.radio("Formato", ["Set Unico", "Best of 3"])
    
    with st.form("iscrizione"):
        a1 = st.selectbox("Atleta 1", [""] + st.session_state.db_atleti + [st.text_input("Nome Nuovo 1")])
        a2 = st.selectbox("Atleta 2", [""] + st.session_state.db_atleti + [st.text_input("Nome Nuovo 2")])
        if st.form_submit_button("ISCRIVI SQUADRA"):
            if a1 and a2:
                name = f"{a1[:3]}-{a2[:3]}".upper()
                st.session_state.teams.append({"name":name, "p1":a1, "p2":a2, "quota":10, "pagato":True})
                if a1 not in st.session_state.db_atleti: st.session_state.db_atleti.append(a1)
                st.rerun()

    st.subheader(f"Squadre Iscritte: {len(st.session_state.teams)}")
    if len(st.session_state.teams) >= 2:
        if st.button("🚀 GENERA TABELLONE E INIZIA", type="primary"):
            st.session_state.matches = simulator.create_calendar(st.session_state.teams)
            st.session_state.phase = "Gironi"
            st.rerun()

elif nav == "Live":
    if st.session_state.phase == "Setup":
        st.warning("Inizia il torneo dal Setup!")
    else:
        st.header("📺 Tabellone Broadcast")
        send_to_rank = st.toggle("Simulazione scrive nel Ranking")
        if st.button("🎲 SIMULA RISULTATI"): 
            simulator.run_simulation(send_to_rank); st.rerun()

        for i, m in enumerate(st.session_state.matches):
            st.markdown(f"""<div class="dazn-card">
                <span class="team-name red-t">{m['A']['name']}</span> 
                <span class="score-display">{m['S1A']} - {m['S1B']}</span> 
                <span class="team-name blue-t">{m['B']['name']}</span>
            </div>""", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1,1,2])
            m['S1A'] = col1.number_input(f"Punti A", 0, 40, m['S1A'], key=f"a{i}")
            m['S1B'] = col2.number_input(f"Punti B", 0, 40, m['S1B'], key=f"b{i}")
            m['Fatto'] = col3.checkbox("Conferma", m['Fatto'], key=f"f{i}")

elif nav == "Ranking":
    ranking_page.show_ranking()
