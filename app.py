import streamlit as st
import random

st.set_page_config(page_title="Beach Volley Pro", layout="centered")

# --- Inizializzazione ---
if 'pos_palla' not in st.session_state:
    st.session_state.pos_palla = 1  # 0: Sinistra, 1: Centro, 2: Destra
if 'score' not in st.session_state:
    st.session_state.score = {"Tu": 0, "CPU": 0}
if 'ultimo_evento' not in st.session_state:
    st.session_state.ultimo_evento = "La partita sta per iniziare! Scegli dove schiacciare."

# --- Funzione per disegnare il campo ---
def disegna_campo(palla_su, pos_palla):
    # Rappresentazione visiva con Emoji
    campo = [["⬜", "⬜", "⬜"], [" ", " ", " "], ["⬜", "⬜", "⬜"]]
    
    # Posizioniamo i giocatori (fissi per ora)
    cpu_pos = 1
    player_pos = 1
    
    # Disegniamo la palla e i giocatori
    campo_visivo = ""
    # Riga CPU
    riga_cpu = ["⬜", "⬜", "⬜"]
    riga_cpu[cpu_pos] = "🤖" # Miniatura CPU
    if palla_su: riga_cpu[pos_palla] = "🏐"
    
    # Rete
    rete = "———— NET ————"
    
    # Riga Player
    riga_player = ["⬜", "⬜", "⬜"]
    riga_player[player_pos] = "👤" # Miniatura Tu
    if not palla_su: riga_player[pos_palla] = "🏐"

    st.markdown(f"### <center>{' '.join(riga_cpu)}</center>", unsafe_allow_html=True)
    st.markdown(f"### <center>{rete}</center>", unsafe_allow_html=True)
    st.markdown(f"### <center>{' '.join(riga_player)}</center>", unsafe_allow_html=True)

# --- Logica di Gioco ---
def gioca(mossa_player):
    mossa_cpu = random.randint(0, 2)
    st.session_state.pos_palla = mossa_player
    
    if mossa_player == mossa_cpu:
        st.session_state.score["CPU"] += 1
        st.session_state.ultimo_evento = "❌ MURATO! La CPU ha previsto la tua mossa."
    else:
        st.session_state.score["Tu"] += 1
        st.session_state.ultimo_evento = "🔥 PUNTO! Hai segnato un ace!"

# --- UI ---
st.title("🏐 Beach Volley Visual")
st.write(f"**Punteggio:** Tu {st.session_state.score['Tu']} | CPU {st.session_state.score['CPU']}")

# Mostra il campo
disegna_campo(palla_su=True, pos_palla=st.session_state.pos_palla)

st.divider()
st.write(f"**Telecronaca:** {st.session_state.ultimo_evento}")

# Pulsanti di movimento
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Schiaccia SX"): gioca(0)
with col2:
    if st.button("Schiaccia Centro"): gioca(1)
with col3:
    if st.button("Schiaccia DX"): gioca(2)

if st.button("Ricomincia"):
    st.session_state.clear()
    st.rerun()
