import streamlit as st
import time
from datetime import datetime

def init_scoreboard_state():
    """Inizializza le variabili per il segnapunti live se non esistono."""
    if 'sb' not in st.session_state:
        st.session_state.sb = {
            "punti_a": 0, "punti_b": 0,
            "set_a": 0, "set_b": 0,
            "battuta": "A", # "A" o "B"
            "start_time": None,
            "match_concluso": False,
            "team_a": "SQUADRA A",
            "team_b": "SQUADRA B"
        }

def pro_scoreboard_ui():
    init_scoreboard_state()
    sb = st.session_state.sb

    st.markdown("""
        <style>
        .main-container { background-color: #0e1117; padding: 20px; border-radius: 20px; }
        .team-red { background: linear-gradient(135deg, #ff4b4b, #a50000); padding: 30px; border-radius: 15px; text-align: center; color: white; border-bottom: 5px solid #ff0000; }
        .team-blue { background: linear-gradient(135deg, #0072ff, #003a80); padding: 30px; border-radius: 15px; text-align: center; color: white; border-bottom: 5px solid #0055ff; }
        .score-val { font-size: 100px; font-weight: bold; font-family: 'Monaco', monospace; line-height: 1; margin: 10px 0; }
        .set-counter { font-size: 24px; background: rgba(0,0,0,0.3); border-radius: 10px; padding: 5px 15px; display: inline-block; }
        .ball-icon { font-size: 30px; color: #fbff00; text-shadow: 0 0 10px #fbff00; }
        .timer-box { font-size: 30px; text-align: center; color: #00ffc3; font-family: 'Courier New'; padding: 10px; border: 1px solid #00ffc3; border-radius: 10px; margin: 10px 0; }
        .btn-plus { font-size: 40px !important; width: 100%; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # Header Match & Timer
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # Gestione Timer
    if sb["start_time"] is None:
        if st.button("⏱️ AVVIA MATCH"):
            sb["start_time"] = time.time()
            st.rerun()
        elapsed = "00:00"
    else:
        now = time.time()
        diff = int(now - sb["start_time"])
        elapsed = f"{diff // 60:02d}:{diff % 60:02d}"

    st.markdown(f"<div class='timer-box'>LIVE CLOCK: {elapsed}</div>", unsafe_allow_html=True)

    # Layout Tabellone
    col1, col_mid, col2 = st.columns([2, 0.5, 2])

    with col1:
        st.markdown(f"""
            <div class='team-red'>
                <h3>{sb['team_a']}</h3>
                <div class='score-val'>{sb['punti_a']}</div>
                <div class='set-counter'>SET: {sb['set_a']}</div>
                <div style='height: 40px;'>{"<span class='ball-icon'>🏐</span>" if sb['battuta'] == 'A' else ""}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("➕ PT RED", use_container_width=True):
            sb["punti_a"] += 1
            sb["battuta"] = "A"
            st.rerun()
        if st.button("➖ PT RED", use_container_width=True):
            sb["punti_a"] = max(0, sb["punti_a"])
            st.rerun()

    with col_mid:
        st.markdown("<h1 style='text-align: center; margin-top: 50px;'>VS</h1>", unsafe_allow_html=True)
        if st.button("🔃", help="Cambio Palla"):
            sb["battuta"] = "B" if sb["battuta"] == "A" else "A"
            st.rerun()

    with col2:
        st.markdown(f"""
            <div class='team-blue'>
                <h3>{sb['team_b']}</h3>
                <div class='score-val'>{sb['punti_b']}</div>
                <div class='set-counter'>SET: {sb['set_b']}</div>
                <div style='height: 40px;'>{"<span class='ball-icon'>🏐</span>" if sb['battuta'] == 'B' else ""}</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("➕ PT BLUE", use_container_width=True):
            sb["punti_b"] += 1
            sb["battuta"] = "B"
            st.rerun()
        if st.button("➖ PT BLUE", use_container_width=True):
            sb["punti_b"] = max(0, sb["punti_b"])
            st.rerun()

    st.write("---")
    
    # Azioni Finalizzazione
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ CHIUDI SET", use_container_width=True):
            if sb["punti_a"] > sb["punti_b"]: sb["set_a"] += 1
            else: sb["set_b"] += 1
            sb["punti_a"], sb["punti_b"] = 0, 0
            st.success("Set Registrato!")
            st.rerun()

    with c2:
        if st.button("🏁 CHIUDI E CONFERMA PARTITA", use_container_width=True):
            # Qui si prepara il dato per app.py
            st.session_state.ready_to_save = {
                "team_a": sb["team_a"],
                "team_b": sb["team_b"],
                "set_a": sb["set_a"],
                "set_b": sb["set_b"]
            }
            st.balloons()
            st.warning("Risultato pronto per l'invio al tabellone del torneo.")
            
    st.markdown("</div>", unsafe_allow_html=True)
