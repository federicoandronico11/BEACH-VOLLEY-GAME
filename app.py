import streamlit as st
from database import init_session, assegna_punti_proporzionali, salva_torneo_storico
from ui_components import load_styles, athlete_selector
import ranking_page, simulator, scoreboard

st.set_page_config(page_title="Zero Skills Cup Pro", layout="wide")
init_session()
load_styles()

# Menu Laterale con Anteprima Ranking
with st.sidebar:
    st.title("🏐 DASHBOARD")
    nav = st.radio("Navigazione", ["Setup Torneo", "Live Scoreboard", "Ranking & Carriera"])
    st.write("---")
    st.subheader("TOP 10 RANKING")
    top_10 = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)[:10]
    for n, p in top_10: st.text(f"{n}: {p} PT")

# 1. SETUP TORNEO
if nav == "Setup Torneo":
    st.header("⚙️ Impostazioni Torneo")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.session_state.settings['formato'] = st.selectbox("Tipologia Tabellone", ["Gironi + Playoff", "Doppia Eliminazione"])
        st.session_state.match_type = st.radio("Formato Match", ["Set Unico", "Best of 3"])
        st.session_state.nome_squadra_auto = st.toggle("Generazione Nome Squadra Automatica", value=True)
    
    with col_s2:
        st.session_state.settings['punti_set'] = st.number_input("Punti per Set", 10, 30, 21)
        st.write(f"🔥 Squadre Iscritte: **{len(st.session_state.teams)}**")
        if st.button("📥 Esporta Storico Incassi (PDF/CSV)"):
            df_incassi = pd.DataFrame(st.session_state.storico_tornei)
            st.download_button("Scarica Dati", df_incassi.to_csv(), "storico_tornei.csv")

    st.write("---")
    # Form Iscrizione
    with st.form("iscrizione_squadra"):
        c1, c2 = st.columns(2)
        with c1: 
            a1_input = st.text_input("Nuovo Atleta 1")
            a1_select = st.selectbox("Oppure seleziona esistente 1", [""] + st.session_state.db_atleti)
        with c2: 
            a2_input = st.text_input("Nuovo Atleta 2")
            a2_select = st.selectbox("Oppure seleziona esistente 2", [""] + st.session_state.db_atleti)
        
        custom_name = st.text_input("Nome Squadra (se manuale)")
        quota = st.number_input("Quota €", 10)
        pagato = st.checkbox("Pagato")
        
        if st.form_submit_button("Iscrivi Squadra"):
            p1 = a1_input if a1_input else a1_select
            p2 = a2_input if a2_input else a2_select
            if p1 and p2:
                name = custom_name if not st.session_state.nome_squadra_auto else f"{p1[:3]}-{p2[:3]}".upper()
                st.session_state.teams.append({"name": name, "p1": p1, "p2": p2, "quota": quota, "pagato": pagato})
                for p in [p1, p2]:
                    if p not in st.session_state.db_atleti: st.session_state.db_atleti.append(p)
                st.rerun()

    if st.button("🚀 INIZIA TORNEO", type="primary"):
        # Logica generazione matches...
        st.session_state.phase = "Gironi"
        st.rerun()

# 2. LIVE SCOREBOARD (TABELLONE TV)
elif nav == "Live Scoreboard":
    scoreboard.pro_scoreboard_ui() # Qui va il tabellone stile DAZN che abbiamo definito

# 3. RANKING
elif nav == "Ranking & Carriera":
    ranking_page.show_ranking_pro()
