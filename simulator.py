import streamlit as st
import random

def generate_volley_score(limit):
    a, b = 0, 0
    while not ((a >= limit or b >= limit) and abs(a - b) >= 2):
        if random.random() > 0.5: a += 1
        else: b += 1
    return a, b

def run_simulation(send_to_rank):
    limit = st.session_state.settings['punti_set']
    tie_limit = st.session_state.settings['punti_tiebreak']
    
    for m in st.session_state.matches:
        if not m['Fatto']:
            # Set 1
            m['S1A'], m['S1B'] = generate_volley_score(limit)
            
            if st.session_state.match_type == "Best of 3":
                # Set 2
                m['S2A'], m['S2B'] = generate_volley_score(limit)
                # Eventuale Tie-break
                sa = (1 if m['S1A'] > m['S1B'] else 0) + (1 if m['S2A'] > m['S2B'] else 0)
                sb = (1 if m['S1B'] > m['S1A'] else 0) + (1 if m['S2B'] > m['S2A'] else 0)
                if sa == 1 and sb == 1:
                    m['S3A'], m['S3B'] = generate_volley_score(tie_limit)
            
            m['Fatto'] = True
            if send_to_rank:
                from database import registra_risultato_completo
                registra_risultato_completo(m)
