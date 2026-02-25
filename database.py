import streamlit as st
from datetime import datetime

def init_session():
    # Database Storici (non si azzerano)
    if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
    if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {}
    if 'db_teams' not in st.session_state: st.session_state['db_teams'] = []
    if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []
    if 'storico_incassi' not in st.session_state: st.session_state['storico_incassi'] = []
    
    # Stato Torneo Corrente (si azzera ogni volta)
    if 'teams' not in st.session_state: st.session_state['teams'] = []
    if 'matches' not in st.session_state: st.session_state['matches'] = []
    if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
    if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"

def registra_incasso_torneo(teams):
    """Calcola il totale incassato dalle squadre con flag 'pagato'."""
    totale = sum(t.get('quota', 0) for t in teams if t.get('pagato', False))
    data_odierna = datetime.now().strftime("%d/%m/%Y %H:%M")
    if totale > 0:
        st.session_state['storico_incassi'].append({
            "Data": data_odierna,
            "Incasso Totale (€)": totale,
            "Squadre Paganti": len([t for t in teams if t.get('pagato', False)])
        })

def assegna_punti_finali(teams):
    """Assegna punti decrescenti a tutti basati sul numero di partecipanti."""
    n = len(teams)
    for i, team in enumerate(teams):
        punti = (n - i) * 10
        for atleta in [team['p1'], team['p2']]:
            st.session_state['ranking_atleti'][atleta] = st.session_state['ranking_atleti'].get(atleta, 0) + punti
