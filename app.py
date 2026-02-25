import streamlit as st
import pandas as pd

# 1. SETUP ESTETICO E COLORI (Nero, Viola, Bianco)
st.set_page_config(page_title="Zero Skills Cup", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Titoli in Viola */
    h1, h2, h3 { color: #9370DB !important; font-family: 'Arial Black', sans-serif; }
    
    /* Stile Payoff */
    .payoff { color: #ffffff; font-style: italic; font-size: 1.2rem; margin-top: -20px; margin-bottom: 30px; }
    
    /* Bottoni Viola */
    .stButton>button {
        background-color: #4B0082;
        color: white;
        border-radius: 8px;
        border: 2px solid #9370DB;
        transition: 0.3s;
    }
    .stButton>button:hover { border: 2px solid #ffffff; background-color: #6a0dad; }
    
    /* Sidebar Dark */
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #4B0082; }
    
    /* Tabelle */
    .stTable { background-color: #1a1a1a; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE STATO (Prevenzione errori KeyError)
if 'teams' not in st.session_state: st.session_state.teams = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'phase' not in st.session_state: st.session_state.phase = "Setup"

# 3. HEADER: LOGO, TITOLO E PAYOFF
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        # Assicurati che il file si chiami logo.png nella cartella principale
        st.image("logo.png", width=160)
    except:
        st.info("Logo non trovato. Carica 'logo.png'.")

with col_title:
    st.title("ZERO SKILLS CUP")
    st.markdown('<p class="payoff">"Se hai 0 skills, sei nel posto giusto"</p>', unsafe_allow_html=True)

# 4. SIDEBAR - GESTIONE TEAM
with st.sidebar:
    st.header("👥 Iscrizioni")
    new_team = st.text_input("Nome Team", placeholder="Es. I Salti Morti", key="input_team")
    if st.button("Aggiungi alla Cup"):
        if new_team and new_team not in st.session_state.teams:
            st.session_state.teams.append(new_team)
            st.rerun()
    
    st.write("---")
    st.write(f"Team iscritti: **{len(st.session_state.teams)}**")
    for t in st.session_state.teams:
        st.text(f"🏐 {t}")

    if len(st.session_state.teams) >= 2 and st.session_state.phase == "Setup":
        if st.button("🚀 AVVIA GIRONE ALL'ITALIANA"):
            st.session_state.phase = "Gironi"
            t = st.session_state.teams
            # Generazione Round Robin (Tutti contro tutti)
            st.session_state.matches = []
            for i in range(len(t)):
                for j in range(i + 1, len(t)):
                    st.session_state.matches.append({
                        "A": t[i], "B": t[j], 
                        "S_A": 0, "S_B": 0, 
                        "Done": False
                    })
            st.rerun()
    
    if st.button("🗑️ Reset Totale"):
        st.session_state.clear()
        st.rerun()

# 5. LOGICA FASE GIRONI
if st.session_state.phase == "Gironi":
    tab_match, tab_classifica = st.tabs(["🎾 Match Day", "📈 Classifica"])
    
    with tab_match:
        st.subheader("Inserimento Risultati")
        for idx, m in enumerate(st.session_state.matches):
            if not m['Done']:
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 2, 1])
                    c1.write(f
