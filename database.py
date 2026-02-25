import streamlit as st

def init_session():
    # Database Storici
    if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
    if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {}
    if 'db_teams' not in st.session_state: st.session_state['db_teams'] = []
    if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []
    
    # Stato Torneo Corrente
    if 'teams' not in st.session_state: st.session_state['teams'] = []
    if 'matches' not in st.session_state: st.session_state['matches'] = []
    if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
    if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"

def assegna_punti_finali(classifica_ordinata):
    """Assegna punti decrescenti a tutti basati sul numero di partecipanti."""
    n = len(classifica_ordinata)
    for i, team in enumerate(classifica_ordinata):
        punti = (n - i) * 10  # Esempio: 1° su 10 prende 100pt, l'ultimo 10pt
        for atleta in [team['p1'], team['p2']]:
            st.session_state['ranking_atleti'][atleta] = st.session_state['ranking_atleti'].get(atleta, 0) + punti
