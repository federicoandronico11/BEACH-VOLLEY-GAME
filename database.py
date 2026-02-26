import streamlit as st

def init_session():
    keys = {
        'db_atleti': [], 'ranking_atleti': {}, 'atleti_stats': {},
        'teams': [], 'matches': [], 'playoffs': [], 'storico_tornei': [],
        'phase': "Setup", 'menu_attivo': "HUB",
        'settings': {"punti_set": 21, "match_type": "Set Unico", "formato": "Gironi + Eliminazione", "richiesta_nome": True}
    }
    for key, val in keys.items():
        if key not in st.session_state: st.session_state[key] = val

def registra_vittoria(team_name, pf, ps, sv, sp):
    # Logica semplificata per aggiornare statistiche nel ranking
    # Verrà chiamata alla conferma di ogni match
    pass
