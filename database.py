import streamlit as st

def init_session():
    # Database persistenti (Atleti, Squadre, Ranking)
    if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
    if 'db_teams' not in st.session_state: st.session_state['db_teams'] = []
    if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {}
    if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []
    
    # Stato del Torneo attuale
    if 'teams' not in st.session_state: st.session_state['teams'] = []
    if 'matches' not in st.session_state: st.session_state['matches'] = []
    if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
    if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
    if 'min_teams' not in st.session_state: st.session_state['min_teams'] = 4
