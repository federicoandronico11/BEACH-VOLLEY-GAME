import streamlit as st

def generate_bracket(teams, mode):
    if mode == "Gironi + Playoff":
        # Logica esistente
        matches = []
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                matches.append({"A": teams[i], "B": teams[j], "SA": 0, "SB": 0, "Fatto": False})
        return matches
    
    elif mode == "Doppia Eliminazione":
        # Struttura base per tabellone vincenti/perdenti
        # Iniziamo con il primo turno del Winner Bracket
        wb_matches = []
        for i in range(0, len(teams), 2):
            if i+1 < len(teams):
                wb_matches.append({"N": f"WB Turno 1 - Match {i//2 + 1}", "A": teams[i], "B": teams[i+1], "SA": 0, "SB": 0, "Fatto": False})
        return wb_matches

def render_match_input(m, key):
    """Inserimento punteggi manuale con aggiornamento automatico"""
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**{m['A']['name']}** vs **{m['B']['name']}**")
    with col2:
        sa = st.number_input("Set A", min_value=0, max_value=2, value=m['SA'], key=f"sa_{key}")
    with col3:
        sb = st.number_input("Set B", min_value=0, max_value=2, value=m['SB'], key=f"sb_{key}")
    
    # Aggiornamento automatico se i set sono inseriti
    if sa != m['SA'] or sb != m['SB']:
        m['SA'] = sa
        m['SB'] = sb
        if sa == 2 or sb == 2:
            m['Fatto'] = True
        st.rerun()
