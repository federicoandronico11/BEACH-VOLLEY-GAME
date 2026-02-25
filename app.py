import streamlit as st
import pandas as pd
from database import init_session, assegna_punti_finali
from ui_components import load_styles, display_sidebar

# 1. SETUP AMBIENTE
st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar()

# 2. FASE SETUP: ISCRIZIONI
if st.session_state['phase'] == "Setup":
    st.title("🏐 CONFIGURAZIONE TORNEO")
    
    # Counter Live
    st.markdown(f"<div class='mega-counter'><h1>{len(st.session_state['teams'])}</h1>Squadre Iscritte</div>", unsafe_allow_html=True)
    
    col_isc, col_list = st.columns([1, 1.2])
    
    with col_isc:
        st.subheader("📝 Iscrizione")
        with st.form("form_isc", clear_on_submit=True):
            usa_nome = st.toggle("Nome squadra personalizzato")
            nome_t = st.text_input("Nome Squadra") if usa_nome else ""
            
            st.write("**Atleta 1**")
            p1_sel = st.selectbox("DB 1", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p1_new = st.text_input("Nuovo Atleta 1", placeholder="Scrivi nome se non in lista", label_visibility="collapsed")
            atleta1 = p1_new if p1_new != "" else p1_sel
            
            st.write("**Atleta 2**")
            p2_sel = st.selectbox("DB 2", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p2_new = st.text_input("Nuovo Atleta 2", placeholder="Scrivi nome se non in lista", label_visibility="collapsed")
            atleta2 = p2_new if p2_new != "" else p2_sel
            
            c_q, c_p = st.columns(2)
            quota = c_q.number_input("Quota (€)", min_value=0, value=10)
            # L'opzione pagamento è legata alla squadra di questo torneo
            pagato = c_p.checkbox("Pagato")
            
            if st.form_submit_button("CONFERMA ISCRIZIONE", use_container_width=True):
                if atleta1 != "-" and atleta2 != "-":
                    nome_def = nome_t if (usa_nome and nome_t != "") else f"{atleta1[:3]}-{atleta2[:3]}".upper()
                    st.session_state['teams'].append({
                        "name": nome_def, "p1": atleta1, "p2": atleta2, 
                        "quota": quota, "pagato": pagato, "full": f"{nome_def} ({atleta1}/{atleta2})"
                    })
                    for a in [atleta1, atleta2]:
                        if a not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a)
                    st.rerun()

    with col_list:
        st.subheader("📋 Lista Squadre")
        for i, t in enumerate(st.session_state['teams']):
            with st.container():
                c1, c2 = st.columns([4, 1])
                p_status = "✅" if t.get('pagato', False) else "❌"
                c1.write(f"{p_status} **{t['full']}**")
                if c2.button("🗑️", key=f"del_{i}"):
                    st.session_state['teams'].pop(i)
                    st.rerun()

        st.write("---")
        if len(st.session_state['teams']) >= 4:
            if st.button("🚀 AVVIA TORNEO A GIRONI", use_container_width=True):
                lt = st.session_state['teams']
                st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False} 
                                               for i in range(len(lt)) for j in range(i+1, len(lt))]
                st.session_state['phase'] = "Gironi"
                st.rerun()

# 3. FASE GIRONI
elif st.session_state['phase'] == "Gironi":
    st.title("🎾 FASE A GIRONI")
    tab_cal, tab_class = st.tabs(["📅 Calendario", "📊 Classifica"])
    
    with tab_cal:
        for i, m in enumerate(st.session_state['matches']):
            with st.expander(f"{m['A']['name']} vs {m['B']['name']} (Risultato: {m['SA']}-{m['SB']})"):
                c1, c2 = st.columns(2)
                m['SA'] = c1.number_input(f"Set {m['A']['name']}", 0, 2, m['SA'], key=f"sa_{i}")
                m['SB'] = c2.number_input(f"Set {m['B']['name']}", 0, 2, m['SB'], key=f"sb_{i}")
                m['Fatto'] = st.checkbox("Match Concluso", m['Fatto'], key=f"f_{i}")

    with tab_class:
        res = {t['full']: {"Punti": 0, "SV": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                res[m['A']['full']]['SV'] += m['SA']
                res[m['B']['full']]['SV'] += m['SB']
                if m['SA'] > m['SB']: res[m['A']['full']]['Punti'] += 3
                else: res[m['B']['full']]['Punti'] += 3
        
        df = pd.DataFrame.from_dict(res, orient='index').reset_index()
        df.columns = ['Squadra', 'Punti', 'Set Vinti']
        df = df.sort_values(["Punti", "Set Vinti"], ascending=False)
        st.table(df)
        
        if st.button("🏆 PROCEDI AI PLAYOFF (TOP 4)"):
            top = [next(t for t in st.session_state['teams'] if t['full'] == name) for name in df['Squadra'][:4]]
            st.session_state['playoffs'] = [
                {"N": "Semi 1 (1° vs 4°)", "A": top[0], "B": top[3], "SA": 0, "SB": 0, "V": None, "L": None},
                {"N": "Semi 2 (2° vs 3°)", "A": top[1], "B": top[2], "SA": 0, "SB": 0, "V": None, "L": None}
            ]
            st.session_state['phase'] = "Playoff"
            st.rerun()

# 4. FASE PLAYOFF E FINALI
elif st.session_state['phase'] == "Playoff":
    st.title("🔥 FASE FINALE")
    
    for i, p in enumerate(st.session_state['playoffs']):
        with st.container():
            st.subheader(p['N'])
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"**{p['A']['name']}** vs **{p['B']['name']}**")
            p['SA'] = c2.number_input(f"Set A", 0, 2, p['SA'], key=f"psa_{i}")
            p['SB'] = c3.number_input(f"Set B", 0, 2, p['SB'], key=f"psb_{i}")
            if p['SA'] == 2 or p['SB'] == 2:
                p['V'] = p['A'] if p['SA'] > p['SB'] else p['B']
                p['L'] = p['B'] if p['SA'] > p['SB'] else p['A']

    if all(p.get('V') for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("✨ GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALE 1° POSTO", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "SA": 0, "SB": 0, "V": None})
            st.session_state['playoffs'].append({"N": "FINALE 3° POSTO", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "SA": 0, "SB": 0, "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.write("---")
        f = st.session_state['playoffs'][2]
        st.header("🏆 " + f['N'])
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"**{f['A']['name']}** vs **{f['B']['name']}**")
        f['SA'] = c2.number_input("Set A", 0, 2, f['SA'], key="final_sa")
        f['SB'] = c3.number_input("Set B", 0, 2, f['SB'], key="final_sb")
        
        if f['SA'] == 2 or f['SB'] == 2:
            vincitore_finale = f['A'] if f['SA'] > f['SB'] else f['B']
            if st.button("🏁 CHIUDI TORNEO E ASSEGNA PUNTI"):
                # Assegnazione punti a tutto il ranking
                assegna_punti_finali(st.session_state['teams']) 
                # Registrazione nell'Albo d'Oro
                st.session_state['albo_oro'].append(f"🏆 {vincitore_finale['name']} ({vincitore_finale['p1']}/{vincitore_finale['p2']})")
                
                # RESET PER IL NUOVO TORNEO:
                # Svuotando 'teams', lo stato dei pagamenti del torneo appena concluso viene azzerato
                st.session_state['teams'] = [] 
                st.session_state['matches'] = []
                st.session_state['playoffs'] = []
                st.session_state['phase'] = "Setup"
                # --- FASE 1: SETUP E ISCRIZIONI ---
if st.session_state['phase'] == "Setup":
    st.title("🏐 CONFIGURAZIONE TORNEO")
    
    # Sezione Cassa Rapida (Nuova)
    incasso_attuale = sum(t.get('quota', 0) for t in st.session_state['teams'] if t.get('pagato', False))
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Squadre Iscritte", len(st.session_state['teams']))
    with c2:
        st.metric("Incasso Corrente", f"{incasso_attuale} €", delta="In cassa")
    with c3:
        if st.button("📊 Vedi Storico Incassi"):
            st.toast("Scorri in basso per lo storico!")

    # Inseriamo una Tab per separare Iscrizioni da Contabilità
    tab_iscrizioni, tab_cassa = st.tabs(["📝 Iscrizioni", "💰 Registro Cassa"])

    with tab_iscrizioni:
        # Qui incolla tutto il codice precedente di col_isc e col_list
        # ... (il form e la lista squadre che hai già) ...

    with tab_cassa:
        st.subheader("Storico Incassi Tornei Conclusi")
        if not st.session_state['storico_incassi']:
            st.info("Nessun torneo archiviato nel registro cassa.")
        else:
            df_cassa = pd.DataFrame(st.session_state['storico_incassi'])
            st.table(df_cassa)
                
                st.balloons()
                st.rerun()
