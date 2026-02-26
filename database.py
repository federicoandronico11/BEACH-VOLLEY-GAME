import streamlit as st
import pandas as pd
from datetime import datetime

def init_session():
    # Inizializzazione di tutte le variabili di stato se non esistono
    keys = {
        'db_atleti': [], 'ranking_atleti': {}, 'atleti_stats': {}, 
        'storico_incassi': [], 'teams': [], 'matches': [], 'playoffs': [],
        'phase': "Setup", 'match_type': "Best of 3",
        'settings': {"punti_set": 21, "punti_tiebreak": 15, "formato": "Gironi + Playoff"}
    }
    for key, val in keys.items():
        if key not in st.session_state:
            st.session_state[key] = val

def registra_risultato_completo(match):
    """Aggiorna le carriere degli atleti basandosi sui risultati del match"""
    for team_key, prefix in [('A', 'S'), ('B', 'S')]:
        team = match[team_key]
        opp_key = 'B' if team_key == 'A' else 'A'
        
        # Calcolo punti fatti/subiti e set vinti/persi
        pf = match['S1'+team_key] + match.get('S2'+team_key, 0) + match.get('S3'+team_key, 0)
        ps = match['S1'+opp_key] + match.get('S2'+opp_key, 0) + match.get('S3'+opp_key, 0)
        
        # Calcolo set vinti
        sv = (1 if match['S1'+team_key] > match['S1'+opp_key] else 0)
        if st.session_state.match_type == "Best of 3":
            sv += (1 if match['S2'+team_key] > match['S2'+opp_key] else 0)
            sv += (1 if match.get('S3'+team_key, 0) > match.get('S3'+opp_key, 0) else 0)
        
        sp = 1 if st.session_state.match_type == "Set Unico" else (2 if sv < 2 else 1 if (match.get('S3A',0) > 0) else 0)
        win = sv >= (1 if st.session_state.match_type == "Set Unico" else 2)

        for atleta in [team['p1'], team['p2']]:
            if atleta in ["", "N/A", "BYE"]: continue
            if atleta not in st.session_state.atleti_stats:
                st.session_state.atleti_stats[atleta] = {"pf":0,"ps":0,"sv":0,"sp":0,"v":0,"p":0,"history":[]}
            
            s = st.session_state.atleti_stats[atleta]
            s['pf'] += pf; s['ps'] += ps; s['sv'] += sv; s['sp'] += sp
            if win: s['v'] += 1
            else: s['p'] += 1
            s['history'].append(pf - ps)

def esporta_storico():
    if not st.session_state.storico_incassi: return None
    return pd.DataFrame(st.session_state.storico_incassi).to_csv(index=False)
