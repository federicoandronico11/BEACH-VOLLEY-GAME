import streamlit as st
import pandas as pd

# 1. SETUP PAGINA
st.set_page_config(page_title="Zero Skills Cup", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #9370DB !important; }
    .stButton>button { background-color: #4B0082; color: white; border-radius: 8px; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #4B0082; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE SICURA
if 'teams' not in st.session_state: st.session_state['teams'] = []
if 'matches' not in st.session_state: st.session_state['matches'] = []
if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"

# 3. HEADER
st.title("ZERO SKILLS CUP")
st.write("Se hai 0 skills, sei nel posto giusto")

# 4. SIDEBAR - GESTIONE TEAM
with st.sidebar:
    st.header("Iscrizioni")
    t_name = st.text_input("Nome Squadra", key="team_name_in")
    p1 = st.text_input("Giocatore 1", key="p1_in")
    p2 = st.text_input("Giocatore 2", key="p2_in")
    
    if st.button("Conferma Iscrizione"):
        if t_name and p1 and p2:
            entry = f"{t_name} ({p1}/{p2})"
            if entry not in st.session_state['teams']:
                st.session_state['teams'].append(entry)
                st.rerun()
    
    st.write("---")
    st.write(f"Squadre: {len(st.session_state['teams'])}")
    for t in st.session_state['teams']:
        st.text(f"🏐 {t}")

    if len(st.session_state['teams']) >= 4 and st.session_state['phase'] == "Setup":
        if st.button("AVVIA TORNEO"):
            st.session_state['phase'] = "Gironi"
            st.session_state['matches'] = []
            lista = st.session_state['teams']
            for i in range(len(lista)):
                for j in range(i + 1, len(lista)):
                    st.session_state['matches'].append({
                        "A":
