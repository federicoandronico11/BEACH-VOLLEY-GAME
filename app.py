import streamlit as st
import pandas as pd
from database import init_session, assegna_punti_finali, registra_incasso_torneo, registra_stats_atleta
from ui_components import load_styles, display_sidebar

st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar()

if st.session_state['phase'] == "Setup":
    st.title("🏐 ZERO SKILLS CUP - CONFIGURAZIONE")
    incasso_attuale = sum(t.get('quota', 0) for t in st.session_state['teams'] if t.get('pagato', False))
    m1, m2, m3 = st.columns(3)
    m1.metric("Squadre Iscritte", len(st.session_state['teams']))
    m2.metric("In Cassa", f"{incasso_attuale} €")
    m3.metric("Tornei Conclusi", len(st.session_state['storico_incassi']))

    tab_isc, tab_cassa = st.tabs(["📝 ISCRIZIONI", "💰 REGISTRO CASSA"])
    with tab_isc:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("isc_form", clear_on_submit=True):
                usa_nome = st.toggle("Nome squadra personalizzato")
                nome_t = st.text_input("Nome Squadra") if usa_nome else ""
                a1 = st.selectbox("Atleta 1", ["-"] + st.session_state['db_atleti'])
                a1_n = st.text_input("Nuovo Atleta 1")
                atleta1 = a1_n if a1_n else a1
                a2 = st.selectbox("Atleta 2", ["-"] + st.session_state['db_atleti'])
                a2_n = st.text_input("Nuovo Atleta 2")
                atleta2 = a2_n if a2_n else a2
                quota = st.number_input("Quota (€)", value=10)
                pagato = st.checkbox("Pagato")
                if st.form_submit_button("Iscrivi"):
                    if atleta1 != "-" and atleta2 != "-":
                        n_def = nome_t if (usa_nome and nome_t) else f"{atleta1[:3]}-{atleta2[:3]}".upper()
                        st.session_state['teams'].append({"name": n_def, "p1": atleta1, "p2": atleta2, "quota": quota, "pagato": pagato, "full": f"{n_def} ({atleta1}/{atleta2})"})
                        if atleta1 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(atleta1)
                        if atleta2 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(atleta2)
                        st.rerun()
        with col2:
            for i, t in enumerate(st.session_state['teams']):
                c1, c2 = st.columns([4, 1])
                c1.write(f"{'✅' if t.get('pagato') else '❌'} **{t['full']}**")
                if c2.button("🗑️", key=f"d_{i}"):
                    st.session_state['teams'].pop(i); st.rerun()
            if len(st.session_state['teams']) >= 4 and st.button("🚀 AVVIA TORNEO"):
                lt = st.session_state['teams']
                st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "S1A":0, "S1B":0, "S2A":0, "S2B":0, "S3A":0, "S3B":0, "Fatto": False} for i in range(len(lt)) for j in range(i+1, len(lt))]
                st.session_state['phase'] = "Gironi"; st.rerun()
    with tab_cassa:
        if st.session_state['storico_incassi']: st.table(pd.DataFrame(st.session_state['storico_incassi']))

elif st.session_state['phase'] == "Gironi":
    st.title("🎾 TABELLONE GIRONI")
    tab_cal, tab_rank = st.tabs(["📅 Inserimento Risultati", "📊 Classifica Avulsa"])
    
    with tab_cal:
        for i, m in enumerate(st.session_state['matches']):
            with st.container():
                st.markdown(f"**MATCH {i+1}: {m['A']['name']} vs {m['B']['name']}**")
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                m['S1A'] = c1.number_input(f"Set 1 - {m['A']['name']}", 0, 30, m['S1A'], key=f"s1a{i}")
                m['S1B'] = c2.number_input(f"Set 1 - {m['B']['name']}", 0, 30, m['S1B'], key=f"s1b{i}")
                m['S2A'] = c1.number_input(f"Set 2 - {m['A']['name']}", 0, 30, m['S2A'], key=f"s2a{i}")
                m['S2B'] = c2.number_input(f"Set 2 - {m['B']['name']}", 0, 30, m['S2B'], key=f"s2b{i}")
                m['S3A'] = c1.number_input(f"Set 3 - {m['A']['name']}", 0, 30, m['S3A'], key=f"s3a{i}")
                m['S3B'] = c2.number_input(f"Set 3 - {m['B']['name']}", 0, 30, m['S3B'], key=f"s3b{i}")
                m['Fatto'] = c3.checkbox("Confermato", m['Fatto'], key=f"f{i}")
                st.write("---")

    with tab_rank:
        # LOGICA CLASSIFICA AVULSA
        stats = {t['full']: {"Punti":0, "SV":0, "SP":0, "PF":0, "PS":0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                # Conteggio Set e Punti Fatti/Subiti
                sa, sb = 0, 0
                if m['S1A'] > m['S1B']: sa += 1; 
                elif m['S1B'] > m['S1A']: sb += 1
                if m['S2A'] > m['S2B']: sa += 1;
                elif m['S2B'] > m['S2A']: sb += 1
                if m['S3A'] > m['S3B'] and (m['S3A']>0 or m['S3B']>0): sa += 1;
                elif m['S3B'] > m['S3A'] and (m['S3A']>0 or m['S3B']>0): sb += 1
                
                stats[m['A']['full']]['SV'] += sa; stats[m['A']['full']]['SP'] += sb
                stats[m['B']['full']]['SV'] += sb; stats[m['B']['full']]['SP'] += sa
                stats[m['A']['full']]['PF'] += (m['S1A'] + m['S2A'] + m['S3A'])
                stats[m['A']['full']]['PS'] += (m['S1B'] + m['S2B'] + m['S3B'])
                stats[m['B']['full']]['PF'] += (m['S1B'] + m['S2B'] + m['S3B'])
                stats[m['B']['full']]['PS'] += (m['S1A'] + m['S2A'] + m['S3A'])
                if sa > sb: stats[m['A']['full']]['Punti'] += 3
                else: stats[m['B']['full']]['Punti'] += 3

        df = pd.DataFrame.from_dict(stats, orient='index').reset_index()
        df['Quoz. Punti'] = (df['PF'] / df['PS'].replace(0, 1)).round(3)
        df = df.sort_values(["Punti", "SV", "Quoz. Punti"], ascending=False)
        st.table(df)
        if st.button("🏆 PASSA AI PLAYOFF"):
            top = [next(t for t in st.session_state['teams'] if t['full'] == n) for n in df['index'][:4]]
            st.session_state['playoffs'] = [{"N": "Semi 1", "A": top[0], "B": top[3], "V": None}, {"N": "Semi 2", "A": top[1], "B": top[2], "V": None}]
            st.session_state['phase'] = "Playoff"; st.rerun()

elif st.session_state['phase'] == "Playoff":
    st.title("🔥 FASE FINALE")
    
    
    
    for i, p in enumerate(st.session_state['playoffs']):
        st.subheader(p['N'])
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"{p['A']['name']} vs {p['B']['name']}")
        win = st.radio(f"Vincitore {p['N']}", ["-", "A", "B"], key=f"pw{i}")
        if win != "-": p['V'] = p['A'] if win == "A" else p['B']; p['L'] = p['B'] if win == "A" else p['A']

    if all(p.get('V') for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALE ORO", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V']})
            st.session_state['playoffs'].append({"N": "FINALE BRONZO", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L']})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        st.write("---")
        for i in range(2, 4):
            f = st.session_state['playoffs'][i]
            st.subheader(f['N'])
            w = st.radio(f"Vincitore {f['N']}", ["-", "A", "B"], key=f"fw{i}")
            if w != "-": f['V'] = f['A'] if w == "A" else f['B']
        
        if st.button("🏁 CHIUDI E SALVA TUTTO"):
            registra_incasso_torneo(st.session_state['teams'])
            assegna_punti_finali(st.session_state['teams'])
            # Salvataggio medaglie e stats (semplificato per brevità)
            vincitore = st.session_state['playoffs'][2]['V']
            st.session_state['albo_oro'].append(f"🏆 {vincitore['name']}")
            registra_stats_atleta(vincitore['p1'], 0, 0, 0, 0, True, 1)
            registra_stats_atleta(vincitore['p2'], 0, 0, 0, 0, True, 1)
            st.session_state['teams'] = []; st.session_state['phase'] = "Setup"; st.balloons(); st.rerun()
