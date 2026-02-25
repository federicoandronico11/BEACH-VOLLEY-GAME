import streamlit as st
import pandas as pd
from database import init_session, assegna_punti_proporzionali
from ui_components import load_styles, display_sidebar_ranking

st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar_ranking()

st.title("🏐 ZERO SKILLS CUP")

if st.session_state['phase'] == "Setup":
    st.markdown(f'<div class="mega-counter"><div class="counter-val">{len(st.session_state["teams"])}</div><div style="color:#9370DB">SQUADRE ISCRITTE</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Iscrizione")
        with st.form("iscrizione_rapida", clear_on_submit=True):
            # Toggle per Nome Squadra
            has_team_name = st.toggle("Personalizza Nome Squadra", value=False)
            team_final = "Team Senza Nome"
            
            if has_team_name:
                c_t1, c_t2 = st.columns(2)
                t_sel = c_t1.selectbox("Esistente", ["-"] + st.session_state['db_teams'], label_visibility="collapsed")
                t_new = c_t2.text_input("Nuovo Nome", placeholder="Nome Squadra", label_visibility="collapsed")
                team_final = t_new if t_new != "" else t_sel
            
            st.write("**Atleti**")
            c1_1, c1_2 = st.columns(2)
            p1_sel = c1_1.selectbox("P1", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p1_new = c1_2.text_input("Nome P1", placeholder="Atleta 1", label_visibility="collapsed")
            p1_final = p1_new if p1_new != "" else p1_sel

            c2_1, c2_2 = st.columns(2)
            p2_sel = c2_1.selectbox("P2", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p2_new = c2_2.text_input("Nome P2", placeholder="Atleta 2", label_visibility="collapsed")
            p2_final = p2_new if p2_new != "" else p2_sel
            
            # Se non c'è un nome squadra, genera uno di default
            if not has_team_name or team_final == "-":
                team_final = f"Coppia {p1_final[:3].upper()}-{p2_final[:3].upper()}"

            if st.form_submit_button("CONFERMA", use_container_width=True):
                if p1_final != "-" and p2_final != "-":
                    st.session_state['teams'].append({
                        "full": f"{team_final} ({p1_final}/{p2_final})",
                        "name": team_final, "p1": p1_final, "p2": p2_final
                    })
                    if team_final not in st.session_state['db_teams']: st.session_state['db_teams'].append(team_final)
                    for p in [p1_final, p2_final]:
                        if p not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(p)
                        if p not in st.session_state['ranking_atleti']: st.session_state['ranking_atleti'][p] = 0
                    st.rerun()

    with col2:
        st.subheader("📋 Check-in")
        for t in st.session_state['teams']: st.write(f"✅ {t['full']}")
        if len(st.session_state['teams']) >= st.session_state['min_teams']:
            if st.button("🚀 AVVIA TORNEO"):
                st.session_state['phase'] = "Gironi"
                lt = st.session_state['teams']
                st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False} for i in range(len(lt)) for j in range(i+1, len(lt))]
                st.rerun()

# --- LOGICA GIRONI E PLAYOFF ---
# (Resta identica alla precedente, ma aggiunge la chiamata a assegna_punti_proporzionali alla fine)

elif st.session_state['phase'] == "Gironi":
    # [Codice gironi precedente...]
    st.header("🎾 GIRONI")
    # ... (inserisci qui la logica gironi del messaggio precedente)

elif st.session_state['phase'] == "Playoff":
    st.header("🏁 FINALI")
    # ... (logica playoff precedente fino alla chiusura torneo)
    
    # MODIFICA FINALE PER ASSEGNARE PUNTI A TUTTI:
    if len(st.session_state['playoffs']) > 2:
        f1 = st.session_state['playoffs'][2]
        winner = st.selectbox("CAMPIONE:", ["-", f1['A']['name'], f1['B']['name']], key="final_w")
        if winner != "-" and st.button("🏁 CHIUDI E CALCOLA PUNTI"):
            # Generiamo una classifica simulata basata sui gironi per dare punti a tutti
            classifica_finale_nomi = [t['full'] for t in st.session_state['teams']] # Esempio semplificato
            assegna_punti_proporzionali(classifica_finale_nomi)
            
            st.session_state['albo_oro'].append(f"🏆 {winner}")
            st.session_state['phase'] = "Setup"
            st.session_state['teams'] = []
            st.balloons()
            st.rerun()
