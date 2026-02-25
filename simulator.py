import streamlit as st
import random

def generate_pro_score(limit):
    a, b = 0, 0
    while not ((a >= limit or b >= limit) and abs(a - b) >= 2):
        if random.random() > 0.5: a += 1
        else: b += 1
    return a, b

def simulate_random_tournament():
    target = st.session_state['matches'] if st.session_state['phase'] == "Gironi" else st.session_state['playoffs']
    limit = st.session_state['settings']['punti_set']
    tie_limit = st.session_state['settings']['punti_tiebreak']

    for m in target:
        if not m.get('Fatto', False):
            if m['B']['name'] == "BYE":
                m['S1A'], m['S1B'], m['Fatto'] = limit, 0, True
                continue
            
            m['S1A'], m['S1B'] = generate_pro_score(limit)
            if st.session_state['match_type'] == "Best of 3":
                m['S2A'], m['S2B'] = generate_pro_score(limit)
                if (m['S1A'] > m['S1B'] and m['S2A'] < m['S2B']) or (m['S1A'] < m['S1B'] and m['S2A'] > m['S2B']):
                    m['S3A'], m['S3B'] = generate_pro_score(tie_limit)
            m['Fatto'] = True
    st.rerun()
