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
                with st.expander(f"🏟️ {m['A']['name']} vs {m['B']['name']}"):
                    ris = st.selectbox("Risultato", ["2-0", "2-1", "1-2", "0-2"], key=f"r{idx}")
                    if st.button("Salva", key=f"btn{idx}"):
                        va, vb = map(int, ris.split("-"))
                        st.session_state['matches'][idx].update({"SA": va, "SB": vb, "Fatto": True})
                        st.rerun()

    with tab2:
        res = {t['full']: {"P": 0, "S": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                res[m['A']['full']]["S"] += m['SA']; res[m['B']['full']]["S"] += m['SB']
                if m['SA'] > m['SB']: res[m['A']['full']]["P"] += 3
                else: res[m['B']['full']]["P"] += 3
        df = pd.DataFrame.from_dict(res, orient='index').reset_index().sort_values(by=["P", "S"], ascending=False)
        st.table(df)

        if all(m['Fatto'] for m in st.session_state['matches']):
            if st.button("🏆 PASSA AI PLAYOFF"):
                top = df["index"].tolist()[:4]
                # Recupero oggetti team
                t_objs = [next(t for t in st.session_state['teams'] if t['full'] == name) for name in top]
                st.session_state['playoffs'] = [
                    {"N": "Semi 1", "A": t_objs[0], "B": t_objs[3], "V": None, "L": None},
                    {"N": "Semi 2", "A": t_objs[1], "B": t_objs[2], "V": None, "L": None}
                ]
                st.session_state['phase'] = "Playoff"
                st.rerun()

# 4. LOGICA PLAYOFF
elif st.session_state['phase'] == "Playoff":
    st.header("🔥 FASE FINALE")
    
    

    c1, c2 = st.columns(2)
    for i in range(2):
        with [c1, c2][i]:
            p = st.session_state['playoffs'][i]
            st.markdown(f"<div class='bracket-box'>{p['A']['name']}<br>vs<br>{p['B']['name']}</div>", unsafe_allow_html=True)
            win = st.selectbox(f"Vincitore {p['N']}", ["-", "Team A", "Team B"], key=f"p{i}")
            if win != "-":
                st.session_state['playoffs'][i]['V'] = p['A'] if win == "Team A" else p['B']
                st.session_state['playoffs'][i]['L'] = p['B'] if win == "Team A" else p['A']

    if all(p['V'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("✨ GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALE 1°", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
            st.session_state['playoffs'].append({"N": "FINALE 3°", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        f1 = st.session_state['playoffs'][2]
        st.markdown(f"<div class='bracket-box' style='border-color:gold;'>ORO: {f1['A']['name']} vs {f1['B']['name']}</div>", unsafe_allow_html=True)
        winner_choice = st.selectbox("CAMPIONE:", ["-", f1['A']['name'], f1['B']['name']], key="final")
        
        if winner_choice != "-" and st.button("🏁 CHIUDI E ASSEGNA PUNTI"):
            vincitore = f1['A'] if winner_choice == f1['A']['name'] else f1['B']
            pts = len(st.session_state['teams']) * 10
            st.session_state['ranking_atleti'][vincitore['p1']] += pts
            st.session_state['ranking_atleti'][vincitore['p2']] += pts
            st.session_state['albo_oro'].append(f"🏆 {vincitore['name']} ({vincitore['p1']}/{vincitore['p2']})")
            st.session_state['phase'] = "Setup"
            st.session_state['teams'] = []
            st.rerun()
