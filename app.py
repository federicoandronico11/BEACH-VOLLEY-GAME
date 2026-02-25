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
        background-color: #4B0082; color: white; border-radius: 8px; border: 2px solid #9370DB; width: 100%;
    }
    .stButton>button:hover { border: 2px solid #ffffff; background-color: #6a0dad; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #4B0082; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE STATO
if 'teams' not in st.session_state: st.session_state.teams = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'playoffs' not in st.session_state: st.session_state.playoffs = []
if 'phase' not in st.session_state: st.session_state.phase = "Setup"

# 3. HEADER
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("📷")
with col_title:
    st.title("ZERO SKILLS CUP")
    st.markdown('<p class="payoff">"Se hai 0 skills, sei nel posto giusto"</p>', unsafe_allow_html=True)

# 4. SIDEBAR
with st.sidebar:
    st.header("👥 Iscrizioni")
    new_team = st.text_input("Nome Team", placeholder="Es. I Salti Morti")
    if st.button("Aggiungi Team"):
        if new_team and new_team not in st.session_state.teams:
            st.session_state.teams.append(new_team)
            st.rerun()
    
    st.write("---")
    if len(st.session_state.teams) >= 4 and st.session_state.phase == "Setup":
        if st.button("🚀 AVVIA FASE GIRONI"):
            st.session_state.phase = "Gironi"
            t = st.session_state.teams
            st.session_state.matches = []
            for i in range(len(t)):
                for j in range(i + 1, len(t)):
                    st.session_state.matches.append({"A": t[i], "B": t[j], "S_A": 0, "S_B": 0, "Done": False})
            st.rerun()
    
    if st.button("🗑️ Reset Totale"):
        st.session_state.clear()
        st.rerun()

# 5. FASE GIRONI
if st.session_state.phase == "Gironi":
    tab1, tab2 = st.tabs(["🎾 Match Day", "📈 Classifica"])
    
    with tab1:
        st.subheader("Risultati Gironi")
        for idx, m in enumerate(st.session_state.matches):
            if not m['Done']:
                c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 2, 1])
                c1.write(f"**{m['A']}**")
                s_a = c2.number_input("Set", 0, 2, key=f"sa_{idx}")
                s_b = c3.number_input("Set", 0, 2, key=f"sb_{idx}")
                c4.write(f"**{m['B']}**")
                if c5.button("OK", key=f"btn_{idx}"):
                    st.session_state.matches[idx]['S_A'] = s_a
                    st.session_state.matches[idx]['S
