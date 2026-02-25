import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_session, assegna_punti_finali, aggiorna_database_storico
from ui_components import load_styles, display_sidebar
import simulator, ranking_page

st.set_page_config(page_title="Zero Skills Cup Pro", layout="wide")
init_session()
load_styles()
nav_mode = display_sidebar()

if nav_mode == "Hall of Fame 🏆":
    ranking_page.show_podium()
    st.stop()

def render_broadcast_match(m, key):
    st.markdown(f"""
    <div class="match-card-broadcast">
        <div class="broadcast-row row-red">🔴 {m['A']['name']}</div>
        <div class="broadcast-row row-blue">🔵 {m['B']['name']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if m['B']['name'] == "BYE":
        st.success("Vittoria Automatica (BYE)")
        m['S1A'], m['S1B'], m['Fatto'] = 21, 0, True
        return m

    c1, c2, c3 = st.columns(3)
    m['S1A'] = c1.number_input("S1 A", 0, 45, m.get('S1A',0), key=f"{key}1a")
    m['S1B'] = c1.number_input("S1 B", 0, 45, m.get('S1B',0), key=f"{key}1b")
    
    if st.session_state.match_type == "Best of 3":
        m['S2A'] = c2.number_input("S2 A", 0, 45, m.get('S2A',0), key=f"{key}2a")
        m['S2B'] = c2.number_input("S2 B", 0, 45, m.get('S2B',0), key=f"{key}2b")
        if (m['S1A']>m['S1B'] and m['S2B']>m['S2A']) or (m['S1B']>m['S1A'] and m['S2A']>m['S2B']):
            m['S3A'] = c3.number_input("S3 A (Tie)", 0, 45, m.get('S3A',0), key=f"{key}3a")
            m['S3B'] = c3.number_input("S3 B (Tie)", 0, 45, m.get('S3B',0), key=f"{key}3b")
    
    m['Fatto'] = st.checkbox("CONFERMA MATCH", m.get('Fatto', False), key=f"{key}f")
    return m

# --- FASE SETUP ---
if st.session_state.phase == "Setup":
    st.title("🏐 SETUP TORNEO")
    
    with st.expander("⚙️ IMPOSTAZIONI TECNICHE", expanded=True):
        c1, c2 = st.columns(2)
        st.session_state.match_type = c1.radio("Formato Match", ["Set Unico", "Best of 3"])
        st.session_state.settings['punti_set'] = c2.number_input("Punti Set", 1, 30, 21)
    
    with st.form("iscrizione", clear_on_submit=True):
        col1, col2 = st.columns(2)
        at1 = col1.text_input("Atleta 1")
        at2 = col2.text_input("Atleta 2")
        if st.form_submit_button("ISCRIVI SQUADRA"):
            if at1 and at2:
                n = f"{at1[:3]}-{at2[:3]}".upper()
                st.session_state.teams.append({"name":n, "p1":at1, "p2":at2, "full":f"{n} ({at1}/{at2})"})
                if at1 not in st.session_state.db_atleti: st.session_state.db_atleti.append(at1)
                if at2 not in st.session_state.db_atleti: st.session_state.db_atleti.append(at2)
                st.rerun()

    st.subheader("Squadre Iscritte")
    for t in st.session_state.teams:
        st.write(f"✅ {t['full']}")
    
    if len(st.session_state.teams) >= 2 and st.button("🚀 GENERA TABELLONE"):
        lt = st.session_state.teams.copy()
        if len(lt) % 2 != 0: lt.append({"name":"BYE", "p1":"N/A", "p2":"N/A"})
        st.session_state.matches = [{"N": f"Gara {i+1}", "A":lt[i], "B":lt[j], "Fatto":False} for i in range(len(lt)) for j in range(i+1, len(lt))]
        st.session_state.phase = "Gironi"; st.rerun()

# --- FASE GIRONI ---
elif st.session_state.phase == "Gironi":
    st.title("🎾 TABELLONE GIRONI")
    if st.button("🎲 SIMULA RISULTATI"): 
        simulator.simulate_random_tournament(); st.rerun()
    
    for i, m in enumerate(st.session_state.matches):
        st.session_state.matches[i] = render_broadcast_match(m, f"g{i}")
    
    # Classifica Analitica
    stats = {t['full']: {"P":0,"SV":0,"SP":0,"PF":0,"PS":0,"obj":t} for t in st.session_state.teams}
    for m in st.session_state.matches:
        if m['Fatto'] and m['B']['name'] != "BYE":
            sa = (1 if m['S1A']>m['S1B'] else 0) + (1 if m.get('S2A',0)>m.get('S2B',0) else 0) + (1 if m.get('S3A',0)>m.get('S3B',0) else 0)
            sb = (1 if m['S1B']>m['S1A'] else 0) + (1 if m.get('S2B',0)>m.get('S2A',0) else 0) + (1 if m.get('S3B',0)>m.get('S3A',0) else 0)
            stats[m['A']['full']]['SV']+=sa; stats[m['A']['full']]['SP']+=sb
            stats[m['B']['full']]['SV']+=sb; stats[m['B']['full']]['SP']+=sa
            stats[m['A']['full']]['PF']+=(m['S1A']+m.get('S2A',0)+m.get('S3A',0))
            stats[m['A']['full']]['PS']+=(m['S1B']+m.get('S2B',0)+m.get('S3B',0))
            stats[m['B']['full']]['PF']+=(m['S1B']+m.get('S2B',0)+m.get('S3B',0))
            stats[m['B']['full']]['PS']+=(m['S1A']+m.get('S2A',0)+m.get('S3A',0))
            if sa > sb: stats[m['A']['full']]['P'] += 3
            else: stats[m['B']['full']]['P'] += 3

    df = pd.DataFrame.from_dict(stats, orient='index').reset_index().sort_values(["P","SV"], ascending=False)
    st.table(df[['index','P','SV','PF','PS']])
    
    if st.button("🏆 VAI AL BRACKET PLAYOFF"):
        top = [stats[n]['obj'] for n in df['index'][:4]]
        st.session_state.playoffs = [
            {"N":"SF1","A":top[0],"B":top[3],"Fatto":False},
            {"N":"SF2","A":top[1],"B":top[2],"Fatto":False}
        ]
        st.session_state.phase = "Playoff"; st.rerun()

# --- FASE PLAYOFF ---
elif st.session_state.phase == "Playoff":
    st.title("🔥 PLAYOFF BRACKET")
    if st.button("🎲 SIMULA PLAYOFF"): simulator.simulate_random_tournament(); st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Semifinali")
        for i in range(2): st.session_state.playoffs[i] = render_broadcast_match(st.session_state.playoffs[i], f"p{i}")
        
    if all(p['Fatto'] for p in st.session_state.playoffs[:2]) and len(st.session_state.playoffs) == 2:
        if st.button("GENERA FINALI"):
            def w(m): return m['A'] if (m['S1A']+m.get('S2A',0)+m.get('S3A',0)) > (m['S1B']+m.get('S2B',0)+m.get('S3B',0)) else m['B']
            st.session_state.playoffs.append({"N":"FINALE","A":w(st.session_state.playoffs[0]),"B":w(st.session_state.playoffs[1]),"Fatto":False})
            st.rerun()

    with col2:
        if len(st.session_state.playoffs) > 2:
            st.subheader("Finale")
            st.session_state.playoffs[2] = render_broadcast_match(st.session_state.playoffs[2], "f1")
            if st.session_state.playoffs[2]['Fatto']:
                if st.button("🏁 CHIUDI TORNEO"):
                    assegna_punti_finali(st.session_state.teams)
                    st.session_state.phase = "Setup"; st.success("Torneo Archiviato!"); st.rerun()
