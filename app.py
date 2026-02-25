import streamlit as st
import pandas as pd

# 1. SETUP ESTETICO
st.set_page_config(page_title="Zero Skills Cup", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #9370DB !important; font-family: 'Arial Black', sans-serif; }
    .payoff { color: #ffffff; font-style: italic; font-size: 1.2rem; margin-top: -20px; margin-bottom: 30px; }
    .stButton>button {
        background-color: #4B0082; color: white; border-radius: 8px; border: 2px solid #9370DB;
    }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #4B0082; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE STATO
if 'teams' not in st.session_state: st.session_state.teams = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'playoffs' not in st.session_state: st.session_state.playoffs = []
if 'phase' not in st.session_state: st.session_state.phase = "Setup"

# 3. HEADER
col_l, col_t = st.columns([1, 4])
with col_l:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("🏐")
with col_t:
    st.title("ZERO SKILLS CUP")
    st.markdown('<p class="payoff">"Se hai 0 skills, sei nel posto giusto"</p>', unsafe_allow_html=True)

# 4. SIDEBAR - AGGIUNTA SQUADRE
with st.sidebar:
    st.header("👥 Iscrizioni 2x2")
    t_name = st.text_input("Nome Team", key="t_input")
    p1 = st.text_input("Giocatore 1", key="p1_input")
    p2 = st.text_input("Giocatore 2", key="p2_input")
    
    if st.button("Aggiungi Team"):
        if t_name and p1 and p2:
            full_entry = f"{t_name} ({p1} - {p2})"
            if full_entry not in st.session_state.teams:
                st.session_state.teams.append(full_entry)
                st.success(f"Aggiunto: {t_name}")
            else:
                st.error("Team già isc
