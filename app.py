import streamlit as st
import pandas as pd

st.set_page_config(page_title="Beach Volley Tournament Manager", layout="wide")

# --- INIZIALIZZAZIONE STATO ---
if 'teams' not in st.session_state:
    st.session_state.teams = []
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'tournament_started' not in st.session_state:
    st.session_state.tournament_started = False

# --- FUNZIONI LOGICHE ---
def add_team(name):
    if name and name not in st.session_state.teams:
        st.session_state.teams.append(name)

def start_tournament(type):
    st.session_state.tournament_started = True
    st.session_state.type = type
    # Qui andrebbe la logica di generazione match (Round Robin o Bracket)
    if not st.session_state.matches:
        generate_initial_matches()

def generate_initial_matches():
    # Esempio semplificato: genera i primi scontri
    t = st.session_state.teams
    if len(t) < 2: return
    for i in range(0, len(t), 2):
        if i+1 < len(t):
            st.session_state.matches.append({"Home": t[i], "Away": t[i+1], "ScoreH": 0, "ScoreA": 0, "Stato": "Da giocare"})

# --- INTERFACCIA UTENTE (UI) ---
st.title("🏐 Beach Volley Tourney Hub")
st.markdown("---")

# SIDEBAR: Configurazione
with st.sidebar:
    st.header("Configurazione Torneo")
    new_team = st.text_input("Aggiungi Team (es. Mario/Luigi)")
    if st.button("Aggiungi"):
        add_team(new_team)
    
    st.write("### Team Iscritti:")
    for team in st.session_state.teams:
        st.text(f"• {team}")
    
    if len(st.session_state.teams) >= 2:
        formula = st.radio("Formula Torneo", ["Gironi + Eliminazione", "Doppia Eliminazione (Pro)"])
        if st.button("Genera Torneo"):
            start_tournament(formula)

# CORPO PRINCIPALE
if not st.session_state.tournament_started:
    st.info("👈 Inserisci almeno due team nella barra laterale e scegli la formula per iniziare.")
else:
    tab1, tab2, tab3 = st.tabs(["📊 Tabellone Match", "📈 Classifica/Bracket", "⚙️ Impostazioni"])

    with tab1:
        st.subheader("Inserimento Risultati")
        for idx, match in enumerate(st.session_state.matches):
            col1, col2, col3, col4 = st.columns([2,1,1,2])
            with col1: st.write(f"**{match['Home']}**")
            with col2: score_h = st.number_input("Set", min_value=0, max_value=2, key=f"h{idx}")
            with col3: score_a = st.number_input("Set", min_value=0, max_value=2, key=f"a{idx}")
            with col4: st.write(f"**{match['Away']}**")
            
            if st.button(f"Conferma Risultato {idx}", key=f"btn{idx}"):
                st.session_state.matches[idx]['ScoreH'] = score_h
                st.session_state.matches[idx]['ScoreA'] = score_a
                st.session_state.matches[idx]['Stato'] = "Finito"
                st.success("Risultato salvato!")

    with tab2:
        st.subheader("Andamento Torneo")
        if st.session_state.type == "Gironi + Eliminazione":
            # Visualizzazione semplice dei risultati
            df = pd.DataFrame(st.session_state.matches)
            st.table(df)
        else:
            st.warning("Visualizzazione Grafica Bracket (Doppia Elim.) in fase di sviluppo.")

    with tab3:
        if st.button("Reset Totale"):
            st.session_state.clear()
            st.rerun()
