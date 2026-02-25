import streamlit as st
import random

def simulate_random_tournament():
    """Simula i risultati per tutti i match della fase corrente."""
    # Determina quali match simulare
    if st.session_state['phase'] == "Gironi":
        target_matches = st.session_state['matches']
    elif st.session_state['phase'] == "Playoff":
        target_matches = st.session_state['playoffs']
    else:
        return

    for m in target_matches:
        if not m.get('Fatto', False):
            if m['B']['name'] == "BYE":
                m['S1A'], m['S1B'], m['Fatto'] = 21, 0, True
                continue

            # Simulazione Set 1
            m['S1A'] = random.randint(15, 21)
            m['S1B'] = 21 if m['S1A'] < 18 else random.randint(10, 19)
            if random.choice([True, False]): m['S1A'], m['S1B'] = m['S1B'], m['S1A']

            if st.session_state.get('match_type') == "Best of 3":
                # Simulazione Set 2
                m['S2A'] = random.randint(15, 21)
                m['S2B'] = 21 if m['S2A'] < 18 else random.randint(10, 19)
                if random.choice([True, False]): m['S2A'], m['S2B'] = m['S2B'], m['S2A']
                
                # Controllo Tie-break
                sa = 1 if m['S1A'] > m['S1B'] else 0
                sa += 1 if m['S2A'] > m['S2B'] else 0
                sb = 1 if m['S1B'] > m['S1A'] else 0
                sb += 1 if m['S2B'] > m['S2A'] else 0
                
                if sa == 1 and sb == 1:
                    m['S3A'] = random.randint(10, 15)
                    m['S3B'] = 15 if m['S3A'] < 12 else random.randint(5, 13)
                    if random.choice([True, False]): m['S3A'], m['S3B'] = m['S3B'], m['S3A']
            
            m['Fatto'] = True
    
    st.toast("🎲 Simulazione completata con successo!", icon="🎰")

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
