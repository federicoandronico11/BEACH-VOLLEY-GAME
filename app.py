import streamlit as st
import pandas as pd
from database import init_session, assegna_punti_finali, registra_incasso_torneo, aggiorna_database_storico
from ui_components import load_styles, display_sidebar

st.set_page_config(page_title="Zero Skills Cup Pro", layout="wide")
init_session()
load_styles()
display_sidebar()

# --- FASE SETUP ---
if st.session_state['phase'] == "Setup":
    st.title("🏐 ZERO SKILLS CUP")
    st.markdown("<div class='mega-counter'><h1>Gara di Beach Volley</h1>Gestione Iscrizioni e Cassa</div>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Iscrizioni", "Registro Cassa"])
    with t1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            with st.form("isc_form"):
                usa_n = st.toggle("Nome squadra custom")
                nome_c = st.text_input("Nome") if usa_n else ""
                a1 = st.selectbox("Atleta 1", ["-"] + st.session_state['db_atleti'])
                a1_n = st.text_input("Nuovo 1")
                at1 = a1_n if a1_n else a1
                a2 = st.selectbox("Atleta 2", ["-"] + st.session_state['db_atleti'])
                a2_n = st.text_input("Nuovo 2")
                at2 = a2_n if a2_n else a2
                q = st.number_input("Quota €", 10)
                p = st.checkbox("Pagato")
                if st.form_submit_button("Iscrivi"):
                    if at1 != "-" and at2 != "-":
                        n = nome_c if (usa_n and nome_c) else f"{at1[:3]}-{at2[:3]}".upper()
                        st.session_state['teams'].append({"name":n, "p1":at1, "p2":at2, "quota":q, "pagato":p, "full":f"{n} ({at1}/{at2})"})
                        if at1 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(at1)
                        if at2 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(at2)
                        st.rerun()
        with c2:
            for i, team in enumerate(st.session_state['teams']):
                st.write(f"{'✅' if team['pagato'] else '❌'} {team['full']}")
            if len(st.session_state['teams']) >= 4 and st.button("🚀 AVVIA TORNEO"):
                lt = st.session_state['teams']
                st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "S1A":0, "S1B":0, "S2A":0, "S2B":0, "S3A":0, "S3B":0, "Fatto": False} for i in range(len(lt)) for j in range(i+1, len(lt))]
                st.session_state['phase'] = "Gironi"; st.rerun()

# --- FASE GIRONI ---
elif st.session_state['phase'] == "Gironi":
    st.title("🎾 GIRONI")
    
    # Visualizzazione moderna dei match
    for i, m in enumerate(st.session_state['matches']):
        with st.expander(f"Match {i+1}: {m['A']['name']} vs {m['B']['name']}"):
            col_a, col_b = st.columns(2)
            m['S1A'] = col_a.number_input(f"S1 {m['A']['name']}", 0, 30, m['S1A'], key=f"1a{i}")
            m['S1B'] = col_b.number_input(f"S1 {m['B']['name']}", 0, 30, m['S1B'], key=f"1b{i}")
            m['S2A'] = col_a.number_input(f"S2 {m['A']['name']}", 0, 30, m['S2A'], key=f"2a{i}")
            m['S2B'] = col_b.number_input(f"S2 {m['B']['name']}", 0, 30, m['S2B'], key=f"2b{i}")
            m['Fatto'] = st.checkbox("Finalizza", m['Fatto'], key=f"f{i}")

    # Calcolo Classifica
    st.write("---")
    stats = {t['full']: {"P":0, "SV":0, "SP":0, "PF":0, "PS":0, "obj":t} for t in st.session_state['teams']}
    for m in st.session_state['matches']:
        if m['Fatto']:
            sa = (1 if m['S1A']>m['S1B'] else 0) + (1 if m['S2A']>m['S2B'] else 0)
            sb = (1 if m['S1B']>m['S1A'] else 0) + (1 if m['S2B']>m['S2A'] else 0)
            stats[m['A']['full']]['SV'] += sa; stats[m['A']['full']]['SP'] += sb
            stats[m['B']['full']]['SV'] += sb; stats[m['B']['full']]['SP'] += sa
            stats[m['A']['full']]['PF'] += (m['S1A']+m['S2A']); stats[m['A']['full']]['PS'] += (m['S1B']+m['S2B'])
            stats[m['B']['full']]['PF'] += (m['S1B']+m['S2B']); stats[m['B']['full']]['PS'] += (m['S1A']+m['S2A'])
            if sa > sb: stats[m['A']['full']]['P'] += 3
            else: stats[m['B']['full']]['P'] += 3

    df = pd.DataFrame.from_dict(stats, orient='index').reset_index().sort_values(["P", "SV"], ascending=False)
    st.table(df[['index', 'P', 'SV', 'PF', 'PS']])
    
    if st.button("🏆 VAI AI PLAYOFF"):
        top_names = df['index'].tolist()[:4]
        top_teams = [stats[name]['obj'] for name in top_names]
        st.session_state['playoffs'] = [
            {"N": "Semi 1", "A": top_teams[0], "B": top_teams[3], "V": None, "L": None},
            {"N": "Semi 2", "A": top_teams[1], "B": top_teams[2], "V": None, "L": None}
        ]
        st.session_state['phase'] = "Playoff"; st.rerun()

# --- FASE PLAYOFF ---
elif st.session_state['phase'] == "Playoff":
    st.title("🔥 PLAYOFF")
    
    
    
    for i, p in enumerate(st.session_state['playoffs']):
        st.subheader(p['N'])
        res = st.radio(f"Vince {p['N']}", ["-", p['A']['name'], p['B']['name']], horizontal=True, key=f"p{i}")
        if res != "-":
            p['V'] = p['A'] if res == p['A']['name'] else p['B']
            p['L'] = p['B'] if res == p['A']['name'] else p['A']

    if all(p.get('V') for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALE 1°", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
            st.session_state['playoffs'].append({"N": "FINALE 3°", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.write("---")
        # Inserimento Vincitori Finali
        f1 = st.session_state['playoffs'][2]
        f3 = st.session_state['playoffs'][3]
        
        c1, c2 = st.columns(2)
        with c1:
            win1 = st.selectbox("🥇 VINCITORE ORO", ["-", f1['A']['name'], f1['B']['name']])
        with c2:
            win3 = st.selectbox("🥉 VINCITORE BRONZO", ["-", f3['A']['name'], f3['B']['name']])

        if win1 != "-" and win3 != "-" and st.button("🏁 CHIUDI E SALVA DATI STORICI"):
            # 1. Registra Cassa
            registra_incasso_torneo(st.session_state['teams'])
            
            # 2. Assegna Punti Ranking Generale
            assegna_punti_finali(st.session_state['teams'])
            
            # 3. Aggiorna Statistiche Individuali di TUTTI gli atleti
            # (Qui simuliamo il piazzamento per dare le medaglie)
            vincitori_oro = f1['A'] if win1 == f1['A']['name'] else f1['B']
            secondi = f1['B'] if win1 == f1['A']['name'] else f1['A']
            terzi = f3['A'] if win3 == f3['A']['name'] else f3['B']
            
            # Funzione di aiuto per salvare i dati degli atleti
            for t in st.session_state['teams']:
                piaz = 1 if t['name'] == vincitori_oro['name'] else (2 if t['name'] == secondi['name'] else (3 if t['name'] == terzi['name'] else 0))
                # Nota: qui potresti integrare i PF/PS reali dai gironi se vuoi la precisione assoluta
                aggiorna_database_storico(t['p1'], 0, 0, 0, 0, (1 if piaz==1 else 0), piaz)
                aggiorna_database_storico(t['p2'], 0, 0, 0, 0, (1 if piaz==1 else 0), piaz)

            st.session_state['albo_oro'].append(f"🏆 {win1} ({datetime.now().strftime('%b %y')})")
            st.session_state['teams'] = []; st.session_state['phase'] = "Setup"; st.balloons(); st.rerun()
