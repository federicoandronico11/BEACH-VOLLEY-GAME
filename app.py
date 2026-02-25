import streamlit as st
from database import init_session
from ui_components import load_styles, display_sidebar_ranking

# 1. Inizializzazione Ambiente
st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar_ranking()

st.title("🏐 ZERO SKILLS CUP")

# 2. LOGICA SETUP (Fase Iscrizioni)
if st.session_state['phase'] == "Setup":
    # Mega Counter in alto
    st.markdown(f'<div class="mega-counter"><div class="counter-val">{len(st.session_state["teams"])}</div><div style="color:#9370DB">SQUADRE ISCRITTE</div></div>', unsafe_allow_html=True)
    
    # Definizione delle Colonne (Risolve il NameError)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Iscrizione Rapida")
        with st.form("iscrizione", clear_on_submit=True):
            # RIGA SQUADRA
            st.write("**Squadra**")
            ct1, ct2 = st.columns(2)
            t_name = ct1.selectbox("Esistente", ["-"] + st.session_state['db_teams'], label_visibility="collapsed")
            t_new = ct2.text_input("Nuova", placeholder="Nuova Squadra", label_visibility="collapsed")
            team_final = t_new if t_new else t_name

            # RIGA ATLETA 1
            st.write("**Atleta 1**")
            ca1, ca2 = st.columns(2)
            p1_sel = ca1.selectbox("P1_E", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p1_new = ca2.text_input("P1_N", placeholder="Nuovo Atleta 1", label_visibility="collapsed")
            p1_final = p1_new if p1_new else p1_sel

            # RIGA ATLETA 2
            st.write("**Atleta 2**")
            cb1, cb2 = st.columns(2)
            p2_sel = cb1.selectbox("P2_E", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p2_new = cb2.text_input("P2_N", placeholder="Nuovo Atleta 2", label_visibility="collapsed")
            p2_final = p2_new if p2_new else p2_sel

            paid = st.checkbox("Quota pagata")
            
            if st.form_submit_button("CONFERMA ISCRIZIONE", use_container_width=True):
                if team_final != "-" and p1_final != "-" and p2_final != "-":
                    st.session_state['teams'].append({
                        "full": f"{team_final} ({p1_final}/{p2_final})", 
                        "name": team_final, "p1": p1_final, "p2": p2_final, "paid": paid
                    })
                    # Aggiorna Database Globale
                    if team_final not in st.session_state['db_teams']: st.session_state['db_teams'].append(team_final)
                    for p in [p1_final, p2_final]:
                        if p not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(p)
                        if p not in st.session_state['ranking_atleti']: st.session_state['ranking_atleti'][p] = 0
                    st.rerun()

    with col2:
        st.subheader("Iscritti")
        for t in st.session_state['teams']:
            color = "🟢" if t['paid'] else "🔴"
            st.write(f"{color} {t['full']}")
        
        st.write("---")
        st.session_state['min_teams'] = st.number_input("Minimo squadre per iniziare:", 4, 32, value=st.session_state['min_teams'])
        
        if len(st.session_state['teams']) >= st.session_state['min_teams']:
            if st.button("🚀 AVVIA TORNEO", use_container_width=True):
                st.session_state['phase'] = "Gironi"
                lt = st.session_state['teams']
                st.session_state['matches'] = []
                for i in range(len(lt)):
                    for j in range(i+1, len(lt)):
                        st.session_state['matches'].append({"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False})
                st.rerun()

# 3. LOGICA GIRONI
elif st.session_state['phase'] == "Gironi":
    st.header("🎾 FASE A GIRONI")
    tab1, tab2 = st.tabs(["Calendario", "Classifica"])
    
    with tab1:
        for idx, m in enumerate(st.session_state['matches']):
            if not m['Fatto']:
                with st.expander(f"🏟️ {m['
