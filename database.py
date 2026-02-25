import streamlit as st

def init_session():
    if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
    if 'db_teams' not in st.session_state: st.session_state['db_teams'] = []
    if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {}
    if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []
    
    if 'teams' not in st.session_state: st.session_state['teams'] = []
    if 'matches' not in st.session_state: st.session_state['matches'] = []
    if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
    if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
    if 'min_teams' not in st.session_state: st.session_state['min_teams'] = 4

def assegna_punti_proporzionali(classifica_finale):
    """
    Assegna punti a TUTTI i partecipanti.
    Formula: (Totale_Squadre - Posizione + 1) * 10
    """
    n_teams = len(classifica_finale)
    for i, team_name in enumerate(classifica_finale):
        posizione = i + 1
        punti = (n_teams - posizione + 1) * 10
        
        # Recupera i nomi degli atleti dal dizionario team
        team_obj = next(t for t in st.session_state['teams'] if t['full'] == team_name)
        atleti = [team_obj['p1'], team_obj['p2']]
        
        for atleta in atleti:
            st.session_state['ranking_atleti'][atleta] = st.session_state['ranking_atleti'].get(atleta, 0) + punti
