import streamlit as st
import pandas as pd
from database import init_session, assegna_punti_finali, registra_incasso_torneo
from ui_components import load_styles, display_sidebar

# 1. SETUP
st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar()

# 2. FASE SETUP
if st.session_state['phase'] == "Setup":
    st.title("🏐 ZERO SKILLS CUP - CONFIGURAZIONE")
    
    # Metriche Cassa e Iscritti
    incasso_attuale = sum(t.get('quota', 0) for t in st.session_state['teams'] if t.get('pagato', False))
    m1, m2, m3 = st.columns(3)
    m1.metric("Squadre Iscritte", len(st.session_state['teams']))
    m2.metric("In Cassa (Torneo Corrente)", f"{incasso_attuale} €")
    m3.metric("Tornei Conclusi", len(st.session_state['storico_incassi']))

    tab_isc, tab_cassa = st.tabs(["📝 ISCRIZIONI", "💰 REGISTRO CASSA STORICO"])

    with tab_isc:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.subheader("Iscrizione")
            with st.form("isc_form", clear_on_submit=True):
                usa_nome = st.toggle("Nome squadra personalizzato")
                nome_t = st.text_input("Nome Squadra") if usa_nome else ""
                
                p1_sel = st.selectbox("Atleta 1 (da DB)", ["-"] + st.session_state['db_atleti'])
                p1_new = st.text_input("Atleta 1 (Nuovo)")
                a1 = p1_new if p1_new != "" else p1_sel
                
                p2_sel = st.selectbox("Atleta 2 (da DB)", ["-"] + st.session_state['db_atleti'])
                p2_new = st.text_input("Atleta 2 (Nuovo)")
                a2 = p2_new if p2_new != "" else p2_sel
                
                c_q, c_p = st.columns(2)
                quota = c_q.number_input("Quota (€)", value=10)
                pagato = c_p.checkbox("Pagato")
                
                if st.form_submit_button("CONFERMA"):
                    if a1 != "-" and a2 != "-":
                        n_def = nome_t if (usa_nome and nome_t != "") else f"{a1[:3]}-{a2[:3]}".upper()
                        st.session_state['teams'].append({
                            "name": n_def, "p1": a1, "p2": a2, "quota": quota, "pagato": pagato, "full": f"{n_def} ({a1}/{a2})"
                        })
                        for a in [a1, a2]:
                            if a not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a)
                        st.rerun()

        with col2:
            st.subheader("Lista Check-in")
            for i, t in enumerate(st.session_state['teams']):
                c1, c2 = st.columns([4, 1])
                st_p = "✅" if t.get('pagato') else "❌"
                c1.write(f"{st_p} **{t['full']}**")
                if c2.button("🗑️", key=f"d_{i}"):
                    st.session_state['teams'].pop(i)
                    st.rerun()
            
            if len(st.session_state['teams']) >= 4:
                if st.button("🚀 AVVIA TORNEO"):
                    lt = st.session_state['teams']
                    st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False} for i in range(len(lt)) for j in range(i+1, len(lt))]
                    st.session_state['phase'] = "Gironi"
                    st.rerun()

    with tab_cassa:
        st.subheader("Registro Incassi Passati")
        if st.session_state['storico_incassi']:
            st.table(pd.DataFrame(st.session_state['storico_incassi']))
        else:
            st.info("Nessun dato registrato.")

# 3. FASE GIRONI
elif st.session_state['phase'] == "Gironi":
    st.title("🎾 GIRONI")
    tab_cal, tab_rank = st.tabs(["Calendario", "Classifica Live"])
    with tab_cal:
        for i, m in enumerate(st.session_state['matches']):
            with st.expander(f"{m['A']['name']} vs {m['B']['name']} ({m['SA']}-{m['SB']})"):
                c1, c2 = st.columns(2)
                m['SA'] = c1.number_input(f"Set {m['A']['name']}", 0, 2, m['SA'], key=f"sa{i}")
                m['SB'] = c2.number_input(f"Set {m['B']['name']}", 0, 2, m['SB'], key=f"sb{i}")
                m['Fatto'] = st.checkbox("Concluso", m['Fatto'], key=f"f{i}")
    with tab_rank:
        res = {t['full']: {"P": 0, "S": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                res[m['A']['full']]['S'] += m['SA']
                res[m['B']['full']]['S'] += m['SB']
                if m['SA'] > m['SB']: res[m['A']['full']]['P'] += 3
                else: res[m['B']['full']]['P'] += 3
        df = pd.DataFrame.from_dict(res, orient='index').reset_index().sort_values(["P", "S"], ascending=False)
        st.table(df)
        if st.button("🏆 PASSA AI PLAYOFF"):
            top = [next(t for t in st.session_state['teams'] if t['full'] == n) for n in df['index'][:4]]
            st.session_state['playoffs'] = [
                {"N": "Semi 1", "A": top[0], "B": top[3], "SA": 0, "SB": 0, "V": None, "L": None},
                {"N": "Semi 2", "A": top[1], "B": top[2], "SA": 0, "SB": 0, "V": None, "L": None}
            ]
            st.session_state['phase'] = "Playoff"
            st.rerun()

# 4. FASE PLAYOFF
elif st.session_state['phase'] == "Playoff":
    st.title("🔥 FASE FINALE")
    
    
    
    for i, p in enumerate(st.session_state['playoffs']):
        st.subheader(p['N'])
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"{p['A']['name']} vs {p['B']['name']}")
        p['SA'] = c2.number_input(f"SA_{i}", 0, 2, p['SA'], label_visibility="collapsed")
        p['SB'] = c3.number_input(f"SB_{i}", 0, 2, p['SB'], label_visibility="collapsed")
        if p['SA'] == 2 or p['SB'] == 2:
            p['V'] = p['A'] if p['SA'] > p['SB'] else p['B']
            p['L'] = p['B'] if p['SA'] > p['SB'] else p['A']

    if all(p.get('V') for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALE 1°", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "SA": 0, "SB": 0})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.write("---")
        f = st.session_state['playoffs'][2]
        st.header("🏆 FINALE ORO")
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"{f['A']['name']} vs {f['B']['name']}")
        f['SA'] = c2.number_input("Final_SA", 0, 2, f['SA'], label_visibility="collapsed")
        f['SB'] = c3.number_input("Final_SB", 0, 2, f['SB'], label_visibility="collapsed")
        
        if (f['SA'] == 2 or f['SB'] == 2) and st.button("🏁 CHIUDI TORNEO"):
            registra_incasso_torneo(st.session_state['teams'])
            assegna_punti_finali(st.session_state['teams'])
            v = f['A'] if f['SA'] > f['SB'] else f['B']
            st.session_state['albo_oro'].append(f"🏆 {v['name']} ({v['p1']}/{v['p2']})")
            st.session_state['teams'] = [] # Azzeramento squadre e pagamenti
            st.session_state['phase'] = "Setup"
            st.balloons()
            st.rerun()
