import streamlit as st
import random

def create_calendar(teams):
    matches = []
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            matches.append({"A": teams[i], "B": teams[j], "Fatto": False})
    return matches

def run_full_sim():
    limit = st.session_state.settings['punti_set']
    for m in st.session_state.matches:
        if not m['Fatto']:
            # Set 1 con scarto di 2
            a = random.randint(18, limit+5)
            b = a - 2 if a > limit else random.randint(10, a-1)
            if random.random() > 0.5: a, b = b, a
            m['S1A'], m['S1B'] = a, b
            m['Fatto'] = True
            
            # Se ON, manda i dati al ranking
            if st.session_state.sim_to_rank:
                from database import aggiorna_statistiche_atleta
                aggiorna_statistiche_atleta(m['A']['p1'], a, b, 1 if a>b else 0, 1 if b>a else 0, a>b)
                aggiorna_statistiche_atleta(m['B']['p1'], b, a, 1 if b>a else 0, 1 if a>b else 0, b>a)
