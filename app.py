import streamlit as st
import pandas as pd
from database import init_session, assegna_punti_finali
from ui_components import load_styles, display_sidebar

st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar()

# --- FASE 1: SETUP E ISCRIZIONI ---
if st.session_state['phase'] == "Setup":
    st.title("🏐 CONFIGURAZIONE TORNEO")
    
    # Counter Live
    st.markdown(f"<div class='mega-counter'><h1>{len(st.session_state['teams'])}</h1>Squadre Iscritte</div>", unsafe_allow_html=True)
    
    col_isc, col_list = st.columns([1, 1.2])
    
    with col_isc:
        st.subheader("Iscrizione")
        with st.form("form_isc", clear_on_submit=True):
            usa_nome = st.toggle("Nome squadra personalizzato")
            nome_t = st.text_input("Nome Squadra") if usa_nome else ""
            
            # Input con suggerimento (Atleti esistenti nel DB)
            p1 = st.selectbox("Atleta 1", [""] + st.session_state['db_atleti'], format_func=lambda x: "Seleziona o scrivi sotto" if x == "" else x)
            p1_new = st.text_input("O nuovo nome Atleta 1")
            atleta1 = p1_new if p1_new else p1
            
            p2 = st.selectbox("Atleta 2", [""] + st.session_state['db_atleti'], format_func=lambda x: "Seleziona o scrivi sotto" if x == "" else x)
            p2_new = st.text_input("O nuovo nome Atleta 2")
            atleta2 = p2_new if p2_new else p2
            
            quota = st.number_input("Quota versata (€)", min_value=0, value=10)
            pagato = st.checkbox("Pagamento ricevuto")
            
            if st.form_submit_button("Iscrivi"):
                if atleta1 and atleta2:
                    nome_def = nome_t if nome_t else f"{atleta1[:3]}-{atleta2[:3]}".upper()
                    st.session_state['teams'].append({
                        "name": nome_def, "p1": atleta1, "p2": atleta2, 
                        "quota": quota, "pagato": pagato, "full": f"{nome_def} ({atleta1}/{atleta2})"
                    })
                    # Salva nel DB atleti se nuovi
                    for a in [atleta1, atleta2]:
                        if a not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a)
                    st.rerun()

    with col_list:
        st.subheader("Lista Squadre")
        for i, t in enumerate(st.session_state['teams']):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"{'✅' if t['pagato'] else '❌'} {t['full']}")
            if c2.button("Modifica", key=f"edit_{i}"):
                st.info("Funzione modifica in arrivo (usa cancella per ora)")
            if c3.button("Elimina", key=f"del_{i}"):
                st.session_state['teams'].pop(i)
                st.rerun()

        st.write("---")
        tipo = st.radio("Tipologia Torneo", ["Gironi + Eliminazione", "Doppia Eliminazione (Coming Soon)"])
        if len(st.session_state['teams']) >= 4:
            if st.button("🚀 AVVIA TORNEO"):
                lt = st.session_state['teams']
                st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False} 
                                               for i in range(len(lt)) for j in range(i+1, len(lt))]
                st.session_state['phase'] = "Gironi"
                st.rerun()

# --- FASE 2: GIRONI ---
elif st.session_state['phase'] == "Gironi":
    st.title("🎾 FASE A GIRONI")
    
    tab_cal, tab_class = st.tabs(["Calendario", "Classifica"])
    
    with tab_cal:
        for i, m in enumerate(st.session_state['matches']):
            with st.expander(f"{m['A']['name']} vs {m['B']['name']} ({m['SA']}-{m['SB']})"):
                c1, c2 = st.columns(2)
                m['SA'] = c1.number_input(f"Set {m['A']['name']}", 0, 2, m['SA'], key=f"sa_{i}")
                m['SB'] = c2.number_input(f"Set {m['B']['name']}", 0, 2, m['SB'], key=f"sb_{i}")
                m['Fatto'] = st.checkbox("Risultato finale", m['Fatto'], key=f"f_{i}")

    with tab_class:
        res = {t['full']: {"Punti": 0, "SV": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                res[m['A']['full']]['SV'] += m['SA']
                res[m['B']['full']]['SV'] += m['SB']
                if m['SA'] > m['SB']: res[m['A']['full']]['Punti'] += 3
                else: res[m['B']['full']]['Punti'] += 3
        
        df = pd.DataFrame.from_dict(res, orient='index').reset_index().sort_values(["Punti", "SV"], ascending=False)
        st.table(df)
        
        if st.button("🏆 PASSA AI PLAYOFF"):
            top = [next(t for t in st.session_state['teams'] if t['full'] == name) for name in df['index'][:4]]
            st.session_state['playoffs'] = [
                {"N": "Semi 1", "A": top[0], "B": top[3], "SA": 0, "SB": 0, "V": None, "L": None},
                {"N": "Semi 2", "A": top[1], "B": top[2], "SA": 0, "SB": 0, "V": None, "L": None}
            ]
            st.session_state['phase'] = "Playoff"
            st.rerun()

# --- FASE 3: ELIMINAZIONE DIRETTA ---
elif st.session_state['phase'] == "Playoff":
    st.title("🔥 FASE ELIMINATORIA")
    
    
    for i, p in enumerate(st.session_state['playoffs']):
        st.subheader(p['N'])
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"{p['A']['name']} vs {p['B']['name']}")
        p['SA'] = c2.number_input(f"Set A", 0, 2, p['SA'], key=f"psa_{i}")
        p['SB'] = c3.number_input(f"Set B", 0, 2, p['SB'], key=f"psb_{i}")
        if p['SA'] == 2 or p['SB'] == 2:
            p['V'] = p['A'] if p['SA'] > p['SB'] else p['B']
            p['L'] = p['B'] if p['SA'] > p['SB'] else p['A']

    if all(p['V'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("Genera Finali"):
            st.session_state['playoffs'].append({"N": "Finale 1-2°", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "SA": 0, "SB": 0, "V": None})
            st.session_state['playoffs'].append({"N": "Finale 3-4°", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "SA": 0, "SB": 0, "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.write("---")
        f = st.session_state['playoffs'][2]
        st.header("🏆 FINALE ORO")
        # Logica risultati finale e tasto chiusura come sopra...
        if st.button("CHIUDI TORNEO E ASSEGNA PUNTI"):
            # Chiamata alla funzione matematica in database.py
            st.session_state['phase'] = "Setup"
            st.balloons()
