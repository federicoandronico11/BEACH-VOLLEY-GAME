import streamlit as st
import pandas as pd
from datetime import datetime

def init_session():
    # Struttura Dati Persistente
    defaults = {
        'db_atleti': [], 'ranking_atleti': {}, 'albo_oro': [], 'storico_incassi': [],
        'atleti_stats': {}, 'teams': [], 'matches': [], 'playoffs': [],
        'phase': "Setup", 'match_type': "Best of 3", 'nome_squadra_auto': True,
        'settings': {
            "punti_set": 21, "punti_tiebreak": 15, 
            "formato": "Gironi + Playoff", "vantaggio": True
        },
        'sim_to_rank': False # Toggle per mandare simulazione a ranking
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def aggiorna_statistiche_atleta(nome, pf, ps, sv, sp, win, pos=None):
    if nome in ["BYE", "N/A", ""]: return
    if nome not in st.session_state.atleti_stats:
        st.session_state.atleti_stats[nome] = {
            "pf": 0, "ps": 0, "sv": 0, "sp": 0, "v": 0, "p": 0, 
            "history": [], "medaglie": []
        }
    s = st.session_state.atleti_stats[nome]
    s['pf'] += pf; s['ps'] += ps; s['sv'] += sv; s['sp'] += sp
    if win: s['v'] += 1
    else: s['p'] += 1
    s['history'].append(pf - ps) # Per i grafici di crescita
    if pos == 1: s['medaglie'].append("🥇")
    elif pos == 2: s['medaglie'].append("🥈")
    elif pos == 3: s['medaglie'].append("🥉")

def esporta_incassi_csv():
    if not st.session_state.storico_incassi: return None
    df = pd.DataFrame(st.session_state.storico_incassi)
    return df.to_csv(index=False).encode('utf-8')
