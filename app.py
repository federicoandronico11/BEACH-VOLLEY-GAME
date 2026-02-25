import streamlit as st
from database import init_session
from ui_components import load_styles, display_sidebar_ranking

# Inizializzazione
st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar_ranking()

st.title("🏐 ZERO SKILLS CUP")

# LOGICA SETUP (ISCRIZIONE)
if st.session_state['phase'] == "Setup":
    st.markdown(f'<div class="mega-counter"><div class="counter-val">{len(st.session_state["teams"])}</div><div style="color:#9370DB">SQUADRE ISCRITTE</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Iscrizione Rapida")
        with st.form("iscrizione", clear_on_submit=True):
            t_name = st.selectbox("Squadra", ["-"] + st.session_state['db_teams'])
            t_new = st.text_input("O nuova squadra")
            team_final = t_new if t_new else t_name

            p1_sel = st.selectbox("Atleta 1", ["-"] + st.session_state['db_atleti'])
            p1_new = st.text_input("O nuovo Atleta 1")
            p1_final = p1_new if p1_new else p1_sel

            p2_sel = st.selectbox("Atleta 2", ["-"] + st.session_state['db_atleti'])
            p2_new = st.text_input("O nuovo Atleta 2")
            p2_final = p2_new if p2_new else p2_sel
            
            if st.form_submit_button("CONFERMA"):
                if team_final != "-" and p1_final != "-" and p2_final != "-":
                    st.session_state['teams'].append({"full": f"{team_final} ({p1_final}/{p2_final})", "name": team_final, "p1": p1_final, "p2": p2_final})
                    # Aggiorna DB
                    if team_final not in st.session_state['db_teams']: st.session_state['db_teams'].append(team_final)
                    for p in [p1_final, p2_final]:
                        if p not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(p)
                        if p not in st.session_state['ranking_atleti']: st.session_state['ranking_atleti'][p] = 0
                    st.rerun()

    with col2:
        st.subheader("Iscritti")
        for t in st.session_state['teams']: st.write(f"✅ {t['full']}")
        if len(st.session_state['teams']) >= st.session_state['min_teams']:
            if st.button("🚀 AVVIA TORNEO"):
                st.session_state['phase'] = "Gironi"
                lt = st.session_state['teams']
                for i in range(len(lt)):
                    for j in range(i+1, len(lt)):
                        st.session_state['matches'].append({"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False})
                st.rerun()

# LOGICA GIRONI (Sintetizzata)
elif st.session_state['phase'] == "Gironi":
    st.subheader("🎾 FASE A GIRONI")
    # Qui inseriremo la tabella match che già conosciamo...
    st.info("Logica Match Day in caricamento...")
    if st.button("Torna al Setup (Debug)"):
        st.session_state['phase'] = "Setup"
        st.rerun()
