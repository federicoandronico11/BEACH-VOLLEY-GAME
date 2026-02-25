import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_session, assegna_punti_finali, registra_incasso_torneo, aggiorna_database_storico, chiudi_torneo_atleta
from ui_components import load_styles, display_sidebar

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Zero Skills Cup Pro", layout="wide")
init_session()
load_styles()
display_sidebar()

def input_match(m, key_prefix):
    """Componente grafico universale per inserire i risultati."""
    with st.container():
        st.markdown(f"**{m.get('N', 'Match')}**: {m['A']['name']} vs {m['B']['name']}")
        c1, c2 = st.columns(2)
        m['S1A'] = c1.number_input(f"S1 {m['A']['name']}", 0, 30, m.get('S1A', 0), key=f"{key_prefix}1a")
        m['S1B'] = c2.number_input(f"S1 {m['B']['name']}", 0, 30, m.get('S1B', 0), key=f"{key_prefix}1b")
        m['S2A'] = c1.number_input(f"S2 {m['A']['name']}", 0, 30, m.get('S2A', 0), key=f"{key_prefix}2a")
        m['S2B'] = c2.number_input(f"S2 {m['B']['name']}", 0, 30, m.get('S2B', 0), key=f"{key_prefix}2b")
        
        # Logica Tie-break
        set_a = (1 if m['S1A'] > m['S1B'] else 0) + (1 if m['S2A'] > m['S2B'] else 0)
        set_b = (1 if m['S1B'] > m['S1A'] else 0) + (1 if m['S2B'] > m['S2A'] else 0)
        
        if set_a == 1 and set_b == 1:
            st.info("Tie-break!")
            m['S3A'] = c1.number_input(f"T3 {m['A']['name']}", 0, 30, m.get('S3A', 0), key=f"{key_prefix}3a")
            m['S3B'] = c2.number_input(f"T3 {m['B']['name']}", 0, 30, m.get('S3B', 0), key=f"{key_prefix}3b")
        else:
            m['S3A'], m['S3B'] = 0, 0
            
        m['Fatto'] = st.checkbox("Confermato", m.get('Fatto', False), key=f"{key_prefix}f")
        st.write("---")
        return m

# --- 2. FASE SETUP ---
if st.session_state['phase'] == "Setup":
    st.title("🏐 ZERO SKILLS CUP")
    st.markdown("<div class='mega-counter'><h1>Configurazione Torneo</h1></div>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Iscrizioni", "Registro Cassa"])
    with t1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            with st.form("isc_form", clear_on_submit=True):
                un = st.toggle("Nome squadra custom")
                nc = st.text_input("Nome Squadra") if un else ""
                a1_n = st.text_input("Atleta 1")
                a2_n = st.text_input("Atleta 2")
                q = st.number_input("Quota €", 10)
                p = st.checkbox("Pagato")
                if st.form_submit_button("Iscrivi"):
                    if a1_n and a2_n:
                        n = nc if (un and nc) else f"{a1_n[:3]}-{a2_n[:3]}".upper()
                        st.session_state['teams'].append({"name":n, "p1":a1_n, "p2":a2_n, "quota":q, "pagato":p, "full":f"{n} ({a1_n}/{a2_n})"})
                        if a1_n not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a1_n)
                        if a2_n not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a2_n)
                        st.rerun()
        with c2:
            st.subheader("Check-in")
            for i, team in enumerate(st.session_state['teams']):
                st.write(f"{'✅' if team['pagato'] else '❌'} {team['full']}")
            if len(st.session_state['teams']) >= 4 and st.button("🚀 AVVIA TORNEO"):
                lt = st.session_state['teams']
                st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "S1A":0, "S1B":0, "S2A":0, "S2B":0, "S3A":0, "S3B":0, "Fatto": False} for i in range(len(lt)) for j in range(i+1, len(lt))]
                st.session_state['phase'] = "Gironi"; st.rerun()
    with t2:
        if st.session_state['storico_incassi']: st.table(pd.DataFrame(st.session_state['storico_incassi']))

# --- 3. FASE GIRONI ---
elif st.session_state['phase'] == "Gironi":
    st.title("🎾 FASE A GIRONI")
    for i, m in enumerate(st.session_state['matches']):
        st.session_state['matches'][i] = input_match(m, f"g{i}")
    
    # Calcolo Classifica
    stats = {t['full']: {"P":0, "SV":0, "SP":0, "PF":0, "PS":0, "obj":t} for t in st.session_state['teams']}
    for m in st.session_state['matches']:
        if m['Fatto']:
            sa = (1 if m['S1A']>m['S1B'] else 0) + (1 if m['S2A']>m['S2B'] else 0) + (1 if m['S3A']>m['S3B'] and (m['S3A']+m['S3B']>0) else 0)
            sb = (1 if m['S1B']>m['S1A'] else 0) + (1 if m['S2B']>m['S2A'] else 0) + (1 if m['S3B']>m['S3A'] and (m['S3A']+m['S3B']>0) else 0)
            stats[m['A']['full']]['SV'] += sa; stats[m['A']['full']]['SP'] += sb
            stats[m['B']['full']]['SV'] += sb; stats[m['B']['full']]['SP'] += sa
            stats[m['A']['full']]['PF'] += (m['S1A']+m['S2A']+m['S3A']); stats[m['A']['full']]['PS'] += (m['S1B']+m['S2B']+m['S3B'])
            stats[m['B']['full']]['PF'] += (m['S1B']+m['S2B']+m['S3B']); stats[m['B']['full']]['PS'] += (m['S1A']+m['S2A']+m['S3A'])
            if sa > sb: stats[m['A']['full']]['P'] += 3
            else: stats[m['B']['full']]['P'] += 3

    df = pd.DataFrame.from_dict(stats, orient='index').reset_index().sort_values(["P", "SV"], ascending=False)
    st.table(df[['index', 'P', 'SV', 'PF', 'PS']])
    
    if st.button("🏆 VAI AL TABELLONE"):
        top_names = df['index'].tolist()[:4]
        top_teams = [stats[name]['obj'] for name in top_names]
        st.session_state['playoffs'] = [
            {"N": "Semifinale 1", "A": top_teams[0], "B": top_teams[3], "S1A":0, "S1B":0, "S2A":0, "S2B":0, "S3A":0, "S3B":0, "Fatto":False},
            {"N": "Semifinale 2", "A": top_teams[1], "B": top_teams[2], "S1A":0, "S1B":0, "S2A":0, "S2B":0, "S3A":0, "S3B":0, "Fatto":False}
        ]
        st.session_state['phase'] = "Playoff"; st.rerun()

# --- 4. FASE PLAYOFF (BRACKET) ---
elif st.session_state['phase'] == "Playoff":
    st.title("🔥 TABELLONE ELIMINATORIA")
    
    col_sf, col_f = st.columns(2)
    
    with col_sf:
        st.subheader("🛡️ Semifinali")
        for i in range(2):
            st.session_state['playoffs'][i] = input_match(st.session_state['playoffs'][i], f"p{i}")
            
        if all(p['Fatto'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
            if st.button("Genera Finali"):
                def win(m): return m['A'] if (m['S1A']+m['S2A']+m['S3A']) > (m['S1B']+m['S2B']+m['S3B']) else m['B']
                def los(m): return m['B'] if (m['S1A']+m['S2A']+m['S3A']) > (m['S1B']+m['S2B']+m['S3B']) else m['A']
                st.session_state['playoffs'].append({"N": "🥇 FINALE 1°", "A": win(st.session_state['playoffs'][0]), "B": win(st.session_state['playoffs'][1]), "S1A":0,"S1B":0,"S2A":0,"S2B":0,"S3A":0,"S3B":0,"Fatto":False})
                st.session_state['playoffs'].append({"N": "🥉 FINALE 3°", "A": los(st.session_state['playoffs'][0]), "B": los(st.session_state['playoffs'][1]), "S1A":0,"S1B":0,"S2A":0,"S2B":0,"S3A":0,"S3B":0,"Fatto":False})
                st.rerun()

    with col_f:
        if len(st.session_state['playoffs']) > 2:
            st.subheader("🏆 Finali")
            for i in range(2, 4):
                st.session_state['playoffs'][i] = input_match(st.session_state['playoffs'][i], f"f{i}")
            
            if all(f['Fatto'] for f in st.session_state['playoffs'][2:]) and st.button("🏁 CHIUDI E SALVA"):
                registra_incasso_torneo(st.session_state['teams'])
                assegna_punti_finali(st.session_state['teams'])
                
                # Salvataggio statistiche per tutti i match
                for m in (st.session_state['matches'] + st.session_state['playoffs']):
                    if m['Fatto']:
                        for a, pf, ps, sv, sp in [
                            (m['A']['p1'], m['S1A']+m['S2A']+m['S3A'], m['S1B']+m['S2B']+m['S3B'], (1 if m['S1A']>m['S1B'] else 0)+(1 if m['S2A']>m['S2B'] else 0)+(1 if m['S3A']>m['S3B'] else 0), (1 if m['S1B']>m['S1A'] else 0)+(1 if m['S2B']>m['S2A'] else 0)+(1 if m['S3B']>m['S3A'] else 0)),
                            (m['A']['p2'], m['S1A']+m['S2A']+m['S3A'], m['S1B']+m['S2B']+m['S3B'], (1 if m['S1A']>m['S1B'] else 0)+(1 if m['S2A']>m['S2B'] else 0)+(1 if m['S3A']>m['S3B'] else 0), (1 if m['S1B']>m['S1A'] else 0)+(1 if m['S2B']>m['S2A'] else 0)+(1 if m['S3B']>m['S3A'] else 0)),
                            (m['B']['p1'], m['S1B']+m['S2B']+m['S3B'], m['S1A']+m['S2A']+m['S3A'], (1 if m['S1B']>m['S1A'] else 0)+(1 if m['S2B']>m['S2A'] else 0)+(1 if m['S3B']>m['S3A'] else 0), (1 if m['S1A']>m['S1B'] else 0)+(1 if m['S2A']>m['S2B'] else 0)+(1 if m['S3A']>m['S3B'] else 0)),
                            (m['B']['p2'], m['S1B']+m['S2B']+m['S3B'], m['S1A']+m['S2A']+m['S3A'], (1 if m['S1B']>m['S1A'] else 0)+(1 if m['S2B']>m['S2A'] else 0)+(1 if m['S3B']>m['S3A'] else 0), (1 if m['S1A']>m['S1B'] else 0)+(1 if m['S2A']>m['S2B'] else 0)+(1 if m['S3A']>m['S3B'] else 0))
                        ]:
                            aggiorna_database_storico(a, pf, ps, sv, sp, 0, 0)
                
                # Medaglie
                f1 = st.session_state['playoffs'][2]
                v_oro = f1['A'] if (f1['S1A']+f1['S2A']+f1['S3A']) > (f1['S1B']+f1['S2B']+f1['S3B']) else f1['B']
                st.session_state['albo_oro'].append(f"🏆 {v_oro['name']} ({datetime.now().strftime('%d/%m')})")
                
                # Incremento tornei
                for t in st.session_state['teams']:
                    chiudi_torneo_atleta(t['p1']); chiudi_torneo_atleta(t['p2'])
                
                st.session_state['teams'] = []; st.session_state['phase'] = "Setup"; st.balloons(); st.rerun()
