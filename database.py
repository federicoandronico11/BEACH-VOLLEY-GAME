import streamlit as st
import pandas as pd
from datetime import datetime

def init_session():
    if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
    if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {}
    if 'atleti_stats' not in st.session_state: st.session_state['atleti_stats'] = {}
    if 'storico_incassi' not in st.session_state: st.session_state['storico_incassi'] = []
    if 'teams' not in st.session_state: st.session_state['teams'] = []
    if 'matches' not in st.session_state: st.session_state['matches'] = []
    if 'phase' not in st.session_state: st.session_state['phase'] = "Setup"
    if 'match_type' not in st.session_state: st.session_state['match_type'] = "Best of 3"
    if 'settings' not in st.session_state:
        st.session_state['settings'] = {"punti_set": 21, "punti_tiebreak": 15, "formato": "Gironi + Playoff"}

def registra_risultato_atleta(nome, pf, ps, sv, sp, win):
    if nome in ["BYE", "N/A", ""]: return
    if nome not in st.session_state.atleti_stats:
        st.session_state.atleti_stats[nome] = {"pf":0,"ps":0,"sv":0,"sp":0,"v":0,"p":0,"history":[]}
    s = st.session_state.atleti_stats[nome]
    s['pf']+=pf; s['ps']+=ps; s['sv']+=sv; s['sp']+=sp
    if win: s['v']+=1 
    else: s['p']+=1
    s['history'].append(pf-ps)

def assegna_punti_ranking(classifica_finale):
    n = len(classifica_finale)
    for i, team_name in enumerate(classifica_finale):
        punti = (n - i) * 10
        team = next(t for t in st.session_state.teams if t['name'] == team_name)
        for atleta in [team['p1'], team['p2']]:
            if atleta != "N/A":
                st.session_state.ranking_atleti[atleta] = st.session_state.ranking_atleti.get(atleta, 0) + punti
