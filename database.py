import streamlit as st

def init_session():
    # Dati Persistenti (Atleti e Ranking)
    if 'db_atleti' not in st.session_state: st.session_state.db_atleti = []
    if 'ranking_atleti' not in st.session_state: st.session_state.ranking_atleti = {}
    if 'atleti_stats' not in st.session_state: st.session_state.atleti_stats = {}
    
    # Stato del Torneo (Temporaneo)
    if 'teams' not in st.session_state: st.session_state.teams = []
    if 'matches' not in st.session_state: st.session_state.matches = []
    if 'playoffs' not in st.session_state: st.session_state.playoffs = []
    if 'phase' not in st.session_state: st.session_state.phase = "Setup"
    
    # Impostazioni
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            "punti_set": 21,
            "match_type": "Set Unico",
            "formato": "Gironi + Playoff"
        }

def assegna_punti_ranking(classifica_finale_nomi):
    """Assegna punti: 1° 100pt, 2° 70pt, 3° 50pt, altri 20pt (Esempio Pro)"""
    premi = {0: 100, 1: 70, 2: 50}
    for i, team_name in enumerate(classifica_finale_nomi):
        pts = premi.get(i, 20)
        # Trova gli atleti del team
        team = next((t for t in st.session_state.teams if t['name'] == team_name), None)
        if team:
            for a in [team['p1'], team['p2']]:
                st.session_state.ranking_atleti[a] = st.session_state.ranking_atleti.get(a, 0) + pts
