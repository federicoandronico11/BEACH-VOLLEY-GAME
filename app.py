import streamlit as st
import random
import time

st.set_page_config(page_title="Beach Volley Cup", layout="centered")

# --- Inizializzazione Stato del Gioco ---
if 'score' not in st.session_state:
    st.session_state.score = {"Player": 0, "CPU": 0}
if 'ball_pos' not in st.session_state:
    st.session_state.ball_pos = "Centro"
if 'message' not in st.session_state:
    st.session_state.message = "Benvenuto alla Beach Volley Cup! Servi per iniziare."

# --- Logica di Gioco ---
def play_round(player_move):
    cpu_move = random.choice(["Sinistra", "Centro", "Destra"])
    
    if player_move == cpu_move:
        st.session_state.score["CPU"] += 1
        st.session_state.message = f"Muro della CPU! Hai tirato a {player_move}, ma la CPU era lì. Punto avversario!"
        st.session_state.ball_pos = "Il campo della CPU"
    else:
        st.session_state.score["Player"] += 1
        st.session_state.message = f"PUNTO! Hai schiacciato a {player_move} e la CPU era a {cpu_move}."
        st.session_state.ball_pos = "Sabbia bollente!"

# --- Interfaccia Grafica ---
st.title("🏐 Beach Volley Online")
st.subheader(f"Punteggio: Tu {st.session_state.score['Player']} - CPU {st.session_state.score['CPU']}")

# Rappresentazione visiva semplificata del campo
st.info(f"Stato della palla: **{st.session_state.ball_pos}**")
st.write(f"💬 {st.session_state.message}")

# Comandi
st.write("### Dove vuoi schiacciare?")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Schiaccia a Sinistra"):
        play_round("Sinistra")
with col2:
    if st.button("Schiaccia al Centro"):
        play_round("Centro")
with col3:
    if st.button("Schiaccia a Destra"):
        play_round("Destra")

if st.button("Reset Partita"):
    st.session_state.score = {"Player": 0, "CPU": 0}
    st.session_state.message = "Partita resettata. Servi!"
    st.rerun()
