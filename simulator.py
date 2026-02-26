import streamlit as st
import random

def create_calendar(teams):
    matches = []
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            matches.append({"A": teams[i], "B": teams[j], "Fatto": False, "S1A":0, "S1B":0, "S2A":0, "S2B":0, "S3A":0, "S3B":0})
    return matches

def run_simulation(to_rank):
    limit = st.session_state.settings['punti_set']
    for m in st.session_state.matches:
        if not m['Fatto']:
            m['S1A'] = random.randint(15, limit+2); m['S1B'] = limit if m['S1A'] < limit else m['S1A']-2
            if random.random() > 0.5: m['S1A'], m['S1B'] = m['S1B'], m['S1A']
            m['Fatto'] = True
            if to_rank:
                from database import registra_risultato_atleta
                win_a = m['S1A'] > m['S1B']
                registra_risultato_atleta(m['A']['p1'], m['S1A'], m['S1B'], 1 if win_a else 0, 1 if not win_a else 0, win_a)
                registra_risultato_atleta(m['B']['p1'], m['S1B'], m['S1A'], 1 if not win_a else 0, 1 if win_a else 0, not win_a)
