import streamlit as st
from datetime import datetime
import pandas as pd

def init_session():
    # Inizializzazione dati persistenti (simulazione salvataggio su disco/DB)
    keys = {
        'db_atleti': [], 'ranking_atleti': {}, 'albo_oro': [], 'storico_tornei': [],
        'atleti_stats': {}, 'teams': [], 'matches': [], 'playoffs': [],
        'phase': "Setup", 'match_type': "Best of 3", 'nome_squadra_auto': True,
        'settings': {"punti_set": 21, "punti_tiebreak": 15, "formato": "Gironi + Playoff"}
    }
    for key, val in keys.items():
        if key not in st.session_state:
            st.session_state[key] = val

def assegna_punti_proporzionali(final_rank):
    """Assegna punti in base al numero di partecipanti: (Tot_Team - Posizione + 1) * 10"""
    n_teams = len(final_rank)
    for i, team_name in enumerate(final_rank):
        punti = (n_teams - i) * 10
        team_data = next(t for t in st.session_state.teams if t['name'] == team_name)
        for atleta in [team_data['p1'], team_data['p2']]:
            if atleta != "N/A":
                st.session_state.ranking_atleti[atleta] = st.session_state.ranking_atleti.get(atleta, 0) + punti

def salva_torneo_storico(vincitore):
    incasso = sum(t['quota'] for t in st.session_state.teams if t.get('pagato', False))
    torneo_info = {
        "Data": datetime.now().strftime("%d/%m/%Y"),
        "Formato": st.session_state.settings['formato'],
        "Partecipanti": len(st.session_state.teams),
        "Incasso": f"{incasso} €",
        "Vincitore": vincitore
    }
    st.session_state.storico_tornei.append(torneo_info)
