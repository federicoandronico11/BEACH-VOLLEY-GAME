import streamlit as st
from datetime import datetime

def init_session():
    # Database Storici (Permanenti nella sessione)
    if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
    if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {}
    if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []
    if 'atleti_stats' not in st.session_state: st.session_state['atleti_stats'] = {}
    
    # Stato Torneo Corrente
    if 'teams' not in st.session_state: st.session_state['teams'] = []
    if 'matches' not in st.session_state: st.session_state['matches'] = []
    if 'playoffs' not in st.session_state: st.session_state['playoffs'] = []
    if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
    if 'match_type' not in st.session_state: st.session_state['match_type'] = "Best of 3"
    
    # Impostazioni Tecniche
    if 'settings' not in st.session_state:
        st.session_state['settings'] = {
            "punti_set": 21,
            "punti_tiebreak": 15,
            "formato_torneo": "Gironi + Playoff",
            "vantaggio_obbligatorio": True
        }

def aggiorna_database_storico(nome_atleta, pf, ps, sv, sp, vittorie, piazzamento):
    if nome_atleta in ["N/A", "BYE", "-"]: return
    if nome_atleta not in st.session_state['atleti_stats']:
        st.session_state['atleti_stats'][nome_atleta] = {
            "pf": 0, "ps": 0, "sv": 0, "sp": 0, 
            "partite_vinte": 0, "tornei_giocati": 0, "medaglie": []
        }
    s = st.session_state['atleti_stats'][nome_atleta]
    s['pf'] += pf; s['ps'] += ps; s['sv'] += sv; s['sp'] += sp
    s['partite_vinte'] += vittorie
    if piazzamento == 1: s['medaglie'].append("🥇")
    elif piazzamento == 2: s['medaglie'].append("🥈")
    elif piazzamento == 3: s['medaglie'].append("🥉")

def assegna_punti_finali(teams):
    n = len(teams)
    for i, team in enumerate(teams):
        punti = (n - i) * 10
        for atleta in [team['p1'], team['p2']]:
            if atleta != "N/A":
                st.session_state['ranking_atleti'][atleta] = st.session_state['ranking_atleti'].get(atleta, 0) + punti
