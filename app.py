import streamlit as st
import database, ui_components, simulator

st.set_page_config(page_title="Z-SKILLS 26", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# --- NAVBAR SUPERIORE ---
st.markdown("<h1 style='text-align: center; color: #00ff85; font-family: Oswald;'>ZERO SKILLS CUP 26</h1>", unsafe_allow_html=True)

# --- HUB PRINCIPALE (MENU FC 26 STYLE) ---
if 'menu_attivo' not in st.session_state: st.session_state.menu_attivo = "HUB"

if st.session_state.menu_attivo == "HUB":
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown('<div class="fc-tile"><h2>GESTIONE</h2><p>Iscrizioni e Setup Torneo</p></div>', unsafe_allow_html=True)
        if st.button("ENTRA SETUP"): 
            st.session_state.menu_attivo = "SETUP"
            st.rerun()

    with cols[1]:
        st.markdown('<div class="fc-tile"><h2>MATCH DAY</h2><p>Risultati Live e Tabellone</p></div>', unsafe_allow_html=True)
        if st.button("VAI AL LIVE"): 
            st.session_state.menu_attivo = "LIVE"
            st.rerun()

    with cols[2]:
        st.markdown('<div class="fc-tile"><h2>CLUB HOUSE</h2><p>Ranking e Carriera Atleti</p></div>', unsafe_allow_html=True)
        if st.button("VEDI RANKING"): 
            st.session_state.menu_attivo = "RANKING"
            st.rerun()

# --- SEZIONE SETUP ---
elif st.session_state.menu_attivo == "SETUP":
    if st.button("⬅️ TORNA ALL'HUB"): st.session_state.menu_attivo = "HUB"; st.rerun()
    
    st.subheader("⚙️ IMPOSTAZIONI TORNEO")
    # Qui inserisci il form iscrizioni professionale (come quello precedente ma con stile FC)
    # ... (Codice Iscrizioni) ...
    
    if len(st.session_state.teams) >= 2:
        if st.button("CONFERMA E GENERA CALENDARIO"):
            # Genera match...
            st.session_state.phase = "Gironi"
            st.session_state.menu_attivo = "LIVE"
            st.rerun()

# --- SEZIONE LIVE (MATCH DAY) ---
elif st.session_state.menu_attivo == "LIVE":
    if st.button("⬅️ TORNA ALL'HUB"): st.session_state.menu_attivo = "HUB"; st.rerun()
    
    st.title("⚽ MATCH DAY - LIVE SCORE")
    
    for i, m in enumerate(st.session_state.matches):
        st.markdown(f"""
        <div class="match-card">
            <div style="flex:1; text-align:right; font-size:1.5rem; font-weight:bold;">{m['A']['name']}</div>
            <div style="margin: 0 30px;"><span class="score-badge">{m['S1A']} - {m['S1B']}</span></div>
            <div style="flex:1; text-align:left; font-size:1.5rem; font-weight:bold; color:#00ff85;">{m['B']['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Campi input invisibili/integrati per i punteggi
        c1, c2, c3 = st.columns([1,1,2])
        m['S1A'] = c1.number_input(f"Score {m['A']['name']}", 0, 45, m['S1A'], key=f"s1a{i}", label_visibility="collapsed")
        m['S1B'] = c2.number_input(f"Score {m['B']['name']}", 0, 45, m['S1B'], key=f"s1b{i}", label_visibility="collapsed")
        m['Fatto'] = c3.checkbox("CONFERMA MATCH", m['Fatto'], key=f"f{i}")

# --- SEZIONE RANKING ---
elif st.session_state.menu_attivo == "RANKING":
    if st.button("⬅️ TORNA ALL'HUB"): st.session_state.menu_attivo = "HUB"; st.rerun()
    # Logica Podio e Carriera...
