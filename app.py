import streamlit as st
import random

st.set_page_config(page_title="Beach Volley Pro", layout="centered")

# --- INIZIALIZZAZIONE SICURA ---
# Usiamo questo blocco per assicurarci che le variabili esistano sempre
if 'score' not in st.session_state:
    st.session_state.score = {"Tu": 0, "CPU": 0}
if 'pos_palla' not in st.session_state:
    st.session_state.pos_palla = 1
if 'ultimo_evento' not in st.session_state:
    st.session_state.ultimo_evento = "Scegli dove schiacciare per iniziare!"

# --- LOGICA DI GIOCO ---
def gioca(mossa_player):
    mossa_cpu = random.randint(0, 2)
    st.session_state.pos_palla = mossa_player
    
    if mossa_player == mossa_cpu:
        st.session_state.score["CPU"] += 1
        st.session_state.ultimo_evento = f"❌ MURO! La CPU era a {['Sinistra', 'Centro', 'Destra'][mossa_cpu]}."
    else:
        st.session_state.score["Tu"] += 1
        st.session_state.ultimo_evento = "🔥 PUNTO! Palla a terra!"

# --- INTERFACCIA ---
st.title("🏐 Beach Volley Visual")

# Visualizzazione Punteggio
punteggio_tu = st.session_state.score.get("Tu", 0)
punteggio_cpu = st.session_state.score.get("CPU", 0)
st.subheader(f"Punteggio: 👤 Tu {punteggio_tu} — 🤖 CPU {punteggio_cpu}")

# --- CAMPO VISIVO ---
def disegna_campo():
    pos = st.session_state.pos_palla
    
    # Creiamo le righe come stringhe di icone
    riga_cpu = ["⬜", "⬜", "⬜"]
    riga_cpu[random.randint(0,2)] = "🤖" # La CPU si muove a caso per estetica
    
    riga_palla = ["  ", "  ", "  "]
    riga_palla[pos] = "🏐"
    
    riga_player = ["⬜", "⬜", "⬜"]
    riga_player[1] = "👤" # Tu sei al centro
    
    # Layout a colonne per centrare il campo
    st.markdown(f"### <center>{' '.join(riga_cpu)}</center>", unsafe_allow_html=True)
    st.write("<center>⎯⎯⎯⎯⎯⎯⎯ NET ⎯⎯⎯⎯⎯⎯⎯</center>", unsafe_allow_html=True)
    st.markdown(f"### <center>{' '.join(riga_palla)}</center>", unsafe_allow_html=True)
    st.markdown(f"### <center>{' '.join(riga_player)}</center>", unsafe_allow_html=True)

disegna_campo()

st.info(st.session_state.ultimo_evento)

# Pulsanti
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Schiaccia SX"): gioca(0)
with col2:
    if st.button("Schiaccia Centro"): gioca(1)
with col3:
    if st.button("Schiaccia DX"): gioca(2)

# --- RESET SICURO ---
if st.button("Ricomincia Partita"):
    # Invece di clear(), resettiamo i valori specifici
    st.session_state.score = {"Tu": 0, "CPU": 0}
    st.session_state.pos_palla = 1
    st.session_state.ultimo_evento = "Nuova partita! Servi tu."
    st.rerun()
