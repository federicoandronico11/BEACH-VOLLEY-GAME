import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_session, assegna_punti_finali, registra_incasso_torneo, aggiorna_database_storico, chiudi_torneo_atleta
from ui_components import load_styles, display_sidebar

st.set_page_config(page_title="Zero Skills Pro", layout="wide")
init_session()
load_styles()
display_sidebar()

# --- WIDGET SEGNAPUNTI DIGITALE ---
def digital_scoreboard():
    if st.session_state['phase'] in ["Gironi", "Playoff"]:
        with st.container():
            st.markdown("<div class='scoreboard-box'>", unsafe_allow_html=True)
            st.subheader("🖥️ SEGNAPUNTI LIVE")
            sc1, sc2, sc3 = st.columns([2, 1, 2])
            
            if 'live_score' not in st.session_state:
                st.session_state.live_score = {"A": 0, "B": 0, "TeamA": "Squadra A", "TeamB": "Squadra B"}

            with sc1:
                st.session_state.live_score["TeamA"] = st.selectbox("Squadra 1", [t['name'] for t in st.session_state['teams']], key="live_a")
                if st.button("➕ PT A"): st.session_state.live_score["A"] += 1; st.rerun()
            with sc2:
                st.markdown(f"<div class='score-font'>{st.session_state.live_score['A']} - {st.session_state.live_score['B']}</div>", unsafe_allow_html=True)
                if st.button("🔄 Reset"): st.session_state.live_score["A"] = 0; st.session_state.live_score["B"] = 0; st.rerun()
            with sc3:
                st.session_state.live_score["TeamB"] = st.selectbox("Squadra 2", [t['name'] for t in st.session_state['teams']], key="live_b")
                if st.button("➕ PT B"): st.session_state.live_score["B"] += 1; st.rerun()
            
            st.info("Usa questo segnapunti per arbitrare. Il risultato finale può essere copiato nei match sottostanti.")
            st.markdown("</div>", unsafe_allow_html=True)

# --- LOGICA MATCH ---
def input_match(m, key_prefix):
    with st.expander(f"Match: {m['A']['name']} vs {m['B']['name']}"):
        if m['B']['name'] == "BYE":
            st.success(f"Vittoria a tavolino per {m['A']['name']}")
            m['S1A'], m['S1B'], m['Fatto'] = 21, 0, True
            return m
            
        c1, c2 = st.columns(2)
        m['S1A'] = c1.number_input(f"Set 1 - {m['A']['name']}", 0, 30, m.get('S1A',0), key=f"{key_prefix}1a")
        m['S1B'] = c2.number_input(f"Set 1 - {m['B']['name']}", 0, 30, m.get('S1B',0), key=f"{key_prefix}1b")
        
        if st.session_state['match_type'] == "Best of 3":
            m['S2A'] = c1.number_input(f"Set 2 - {m['A']['name']}", 0, 30, m.get('S2A',0), key=f"{key_prefix}2a")
            m['S2B'] = c2.number_input(f"Set 2 - {m['B']['name']}", 0, 30, m.get('S2B',0), key=f"{key_prefix}2b")
            if ((m['S1A']>m['S1B'] and m['S2B']>m['S2A']) or (m['S1B']>m['S1A'] and m['S2A']>m['S2B'])):
                m['S3A'] = c1.number_input(f"Tie-break - {m['A']['name']}", 0, 30, m.get('S3A',0), key=f"{key_prefix}3a")
                m['S3B'] = c2.number_input(f"Tie-break - {m['B']['name']}", 0, 30, m.get('S3B',0), key=f"{key_prefix}3b")
        
        m['Fatto'] = st.checkbox("Salva Risultato", m.get('Fatto', False), key=f"{key_prefix}f")
        return m

# --- FASE SETUP ---
if st.session_state['phase'] == "Setup":
    st.title("🏐 ZERO SKILLS CUP - CONFIGURAZIONE")
    st.session_state['match_type'] = st.radio("Tipologia Partite", ["Set Unico", "Best of 3"])
    
    with st.form("isc_form"):
        at1 = st.text_input("Atleta 1"); at2 = st.text_input("Atleta 2")
        if st.form_submit_button("Iscrivi Squadra"):
            if at1 and at2:
                n = f"{at1[:3]}-{at2[:3]}".upper()
                st.session_state['teams'].append({"name":n, "p1":at1, "p2":at2, "full":f"{n} ({at1}/{at2})"})
                st.rerun()
    
    for t in st.session_state['teams']: st.write(f"✅ {t['full']}")
    
    if len(st.session_state['teams']) >= 3 and st.button("AVVIA TORNEO"):
        # Logica BYE Automatica
        lt = st.session_state['teams'].copy()
        if len(lt) % 2 != 0:
            lt.append({"name": "BYE", "p1": "N/A", "p2": "N/A"})
        
        st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "Fatto": False} for i in range(len(lt)) for j in range(i+1, len(lt))]
        st.session_state['phase'] = "Gironi"; st.rerun()

# --- FASE GIRONI ---
elif st.session_state['phase'] == "Gironi":
    digital_scoreboard()
    st.title("🎾 GIRONI")
    for i, m in enumerate(st.session_state['matches']):
        st.session_state['matches'][i] = input_match(m, f"g{i}")
    
    if st.button("🏆 VAI AI PLAYOFF"):
        st.session_state['phase'] = "Playoff"
        # Logica selezione top 4... (come versioni precedenti)
        st.rerun()

# --- FASE PLAYOFF ---
elif st.session_state['phase'] == "Playoff":
    digital_scoreboard()
    # (Logica tabellone bracket come versione precedente...)
    # In caso di vittoria finale:
    if st.session_state.get('torneo_concluso'):
        st.markdown(f"""
        <div class='winner-announcement'>
            <h1>🏆 CAMPIONI TORNEO 🏆</h1>
            <h2>{st.session_state['winner_name']}</h2>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        if st.button("CHIUDI E TORNA AL SETUP"):
            st.session_state['phase'] = "Setup"
            st.rerun()
