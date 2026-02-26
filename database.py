import streamlit as st

def init_session():
    keys = {
        'db_atleti': [], 
        'ranking_atleti': {}, 
        'atleti_stats': {},
        'teams': [], 
        'matches': [], 
        'playoffs': [], 
        'albo_oro': [],
        'phase': "Setup", 
        'menu_attivo': "HUB",
        'settings': {"punti_set": 21, "match_type": "Set Unico", "formato": "Gironi + Eliminazione"}
    }
    for key, val in keys.items():
        if key not in st.session_state: st.session_state[key] = val

def aggiorna_carriera(team, pf, ps, win, sv, sp):
    """Aggiorna i dati analitici di ogni atleta del team dopo un match"""
    for atleta in [team['p1'], team['p2']]:
        if atleta not in st.session_state.atleti_stats:
            st.session_state.atleti_stats[atleta] = {
                "pf":0, "ps":0, "sv":0, "sp":0, "v":0, "p":0, 
                "medaglie": 0, "history": []
            }
        
        s = st.session_state.atleti_stats[atleta]
        s['pf'] += pf
        s['ps'] += ps
        s['sv'] += sv
        s['sp'] += sp
        
        if win: 
            s['v'] += 1
            st.session_state.ranking_atleti[atleta] = st.session_state.ranking_atleti.get(atleta, 0) + 10
        else: 
            s['p'] += 1
            st.session_state.ranking_atleti[atleta] = st.session_state.ranking_atleti.get(atleta, 0) + 2
        
        s['history'].append(pf - ps)
