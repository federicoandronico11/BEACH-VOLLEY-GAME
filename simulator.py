import streamlit as st
import random

def generate_pro_score(limit):
    a, b = 0, 0
    while not ((a >= limit or b >= limit) and abs(a - b) >= 2):
        if random.random() > 0.5: a += 1
        else: b += 1
    return a, b

def simulate_random_tournament():
    phase = st.session_state['phase']
    target = st.session_state['matches'] if phase == "Gironi" else st.session_state['playoffs']
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
                s_a = (1 if m['S1A'] > m['S1B'] else 0) + (1 if m['S2A'] > m['S2B'] else 0)
                s_b = (1 if m['S1B'] > m['S1A'] else 0) + (1 if m['S2B'] > m['S2A'] else 0)
                if s_a == 1 and s_b == 1:
                    m['S3A'], m['S3B'] = generate_pro_score(tie_limit)
            m['Fatto'] = True
    st.toast("🎲 Simulazione completata!")
