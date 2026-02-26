import streamlit as st

def init_session():
    # Inizializza tutti i contenitori senza sovrascriverli se esistono già
    if 'db_atleti' not in st.session_state: st.session_state.db_atleti = []
    if 'ranking_atleti' not in st.session_state: st.session_state.ranking_atleti = {}
    if 'atleti_stats' not in st.session_state: st.session_state.atleti_stats = {}
    if 'teams' not in st.session_state: st.session_state.teams = []
    if 'matches' not in st.session_state: st.session_state.matches = []
    if 'playoffs' not in st.session_state: st.session_state.playoffs = []
    if 'phase' not in st.session_state: st.session_state.phase = "Setup"
    if 'menu_attivo' not in st.session_state: st.session_state.menu_attivo = "HUB"
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            "punti_set": 21, 
            "match_type": "Set Unico", 
            "formato": "Gironi + Eliminazione",
            "punti_tiebreak": 15
        }

def aggiorna_carriera(team, pf, ps, win, sv, sp):
    """Aggiorna i dati analitici di ogni atleta del team e registra il log del match"""
    
    # Identifichiamo il nome del team avversario per il log (opzionale, ma utile per la carriera)
    # Cerchiamo di capire chi è l'avversario dai match correnti se necessario, 
    # ma per ora usiamo un placeholder generico o il nome del team.
    
    for atleta in [team['p1'], team['p2']]:
        if atleta not in st.session_state.atleti_stats:
            st.session_state.atleti_stats[atleta] = {
                "pf":0, "ps":0, "sv":0, "sp":0, "v":0, "p":0, 
                "medaglie": 0, "history": [], "match_logs": [] # Aggiunto match_logs
            }
        
        s = st.session_state.atleti_stats[atleta]
        s['pf'] += pf
        s['ps'] += ps
        s['sv'] += sv
        s['sp'] += sp
        
        # --- NUOVA LOGICA LOG MATCH ---
        esito = "Vittoria" if win else "Sconfitta"
        # Registriamo il log del match per la visualizzazione nella Hall of Fame
        s['match_logs'].append({
            "esito": esito,
            "punteggio": f"{pf}-{ps}",
            "avversario": "Match Torneo" # Identificativo generico
        })
        # ------------------------------
        
        if win: 
            s['v'] += 1
            st.session_state.ranking_atleti[atleta] = st.session_state.ranking_atleti.get(atleta, 0) + 10
        else: 
            s['p'] += 1
            st.session_state.ranking_atleti[atleta] = st.session_state.ranking_atleti.get(atleta, 0) + 2
        
        s['history'].append(pf - ps)
