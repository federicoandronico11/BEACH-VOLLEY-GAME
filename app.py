import streamlit as st
from ui_components import load_css, mega_counter
from database import init_db, save_atleta

# Inizializzazione
st.set_page_config(page_title="Zero Skills Cup", layout="wide")
load_css()
init_db()

# Sidebar con Ranking Live (CONFERMATO)
with st.sidebar:
    st.title("📊 LIVE RANKING")
    sorted_rank = sorted(st.session_state['ranking_atleti'].items(), key=lambda x: x[1], reverse=True)
    for i, (name, pts) in enumerate(sorted_rank):
        st.markdown(f"<div class='ranking-row'><span>{name}</span><span>{pts}</span></div>", unsafe_allow_html=True)

# Qui inizieremo a scrivere solo le NUOVE modifiche
st.title("🏐 ZERO SKILLS CUP")
# ... resto della logica ...
