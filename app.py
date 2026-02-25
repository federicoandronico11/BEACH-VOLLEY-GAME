import streamlit as st
from database import init_session, assegna_punti_proporzionali
from ui_components import load_styles, display_sidebar_ranking
from tournament_engine import generate_bracket, render_match_input

st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar_ranking()

if st.session_state['phase'] == "Setup":
    st.title("🏐 ISCRIZIONI E CONFIGURAZIONE")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("iscrizione_form"):
            # MODIFICA: Toggle Nome Squadra
            usa_nome = st.toggle("Usa Nome Squadra Personalizzato")
            t_final = "Team"
            if usa_nome:
                t_final = st.text_input("Nome Squadra")
            
            st.write("---")
            c1, c2 = st.columns(2)
            p1 = c1.text_input("Atleta 1")
            p2 = c2.text_input("Atleta 2")
            
            if not usa_nome:
                t_final = f"{p1[:3]}-{p2[:3]}".upper() if p1 and p2 else "Nuovo Team"

            if st.form_submit_button("Iscrivi Squadra"):
                if p1 and p2:
                    st.session_state['teams'].append({"name": t_final, "p1": p1, "p2": p2, "full": f"{t_final} ({p1}/{p2})"})
                    st.rerun()

    with col2:
        st.subheader("Impostazioni Torneo")
        # MODIFICA: Scelta Tipologia Tabellone
        tipo_torneo = st.radio("Tipologia di Tabellone", ["Gironi + Playoff", "Doppia Eliminazione"])
        
        st.write(f"Squadre iscritte: {len(st.session_state['teams'])}")
        for t in st.session_state['teams']:
            st.write(f"✅ {t['full']}")
            
        if len(st.session_state['teams']) >= 4:
            if st.button("🚀 AVVIA TORNEO"):
                st.session_state['matches'] = generate_bracket(st.session_state['teams'], tipo_torneo)
                st.session_state['tournament_mode'] = tipo_torneo
                st.session_state['phase'] = "Torneo"
                st.rerun()

elif st.session_state['phase'] == "Torneo":
    st.header(f"🏆 FASE: {st.session_state['tournament_mode']}")
    
    if st.session_state['tournament_mode'] == "Doppia Eliminazione":
        st.info("Visualizzazione Tabellone Doppia Eliminazione")
        
    
    # Visualizzazione Match con inserimento automatico
    for i, m in enumerate(st.session_state['matches']):
        if not m['Fatto']:
            render_match_input(m, i)
    
    st.write("---")
    if st.button("🔙 Torna al Setup"):
        st.session_state['phase'] = "Setup"
        st.rerun()
