import streamlit as st
from datetime import datetime

def init_session():
    # Database Storici (Permanenti)
    if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
    if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {}
    if 'db_teams' not in st.session_state: st.session_state['db_teams'] = []
    if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []
    if 'storico_incassi' not in st.session_state: st.session_state['storico_incassi'] = []
    
    # Statistiche Atleta (Nuovo)
    if 'atleti_stats' not in st.session_state: st.session_state['atleti_stats'] = {}
    
    # Stato Torneo Corrente
    if 'teams' not in st.session_state: st.session_state['teams'] = []
    if 'matches' not in st.session_state: st.session_state['matches'] = []
    if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
    if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"

def registra_stats_atleta(nome, pf, ps, sv, sp, vinto, piazzamento):
    """Aggiorna lo storico dell'atleta."""
    if nome not in st.session_state['atleti_stats']:
        st.session_state['atleti_stats'][nome] = {
            "pf": 0, "ps": 0, "sv": 0, "sp": 0, "partite": 0, "medaglie": []
        }
    s = st.session_state['atleti_stats'][nome]
    s['pf'] += pf
    s['ps'] += ps
    s['sv'] += sv
    s['sp'] += sp
    s['partite'] += 1
    if piazzamento == 1: s['medaglie'].append("🥇")
    elif piazzamento == 2: s['medaglie'].append("🥈")
    elif piazzamento == 3: s['medaglie'].append("🥉")

def registra_incasso_torneo(teams):
    totale = sum(t.get('quota', 0) for t in teams if t.get('pagato', False))
    data_odierna = datetime.now().strftime("%d/%m/%Y %H:%M")
    if totale > 0:
        st.session_state['storico_incassi'].append({
            "Data": data_odierna, "Incasso Totale (€)": totale,
            "Squadre Paganti": len([t for t in teams if t.get('pagato', False)])
        })

def assegna_punti_finali(teams):
    n = len(teams)
    for i, team in enumerate(teams):
        punti = (n - i) * 10
        for atleta in [team['p1'], team['p2']]:
            st.session_state['ranking_atleti'][atleta] = st.session_state['ranking_atleti'].get(atleta, 0) + punti
