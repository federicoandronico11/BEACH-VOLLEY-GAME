import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_session, assegna_punti_finali, registra_incasso_torneo, aggiorna_database_storico, chiudi_torneo_atleta
from ui_components import load_styles, display_sidebar

st.set_page_config(page_title="Zero Skills Cup Pro", layout="wide")
init_session()
load_styles()
display_sidebar()

def input_match(m, key_prefix):
    with st.container():
        st.markdown(f"**{m['N']}**")
        c1, c2 = st.columns(2)
        m['S1A'] = c1.number_input(f"S1 {m['A']['name']}", 0, 30, m.get('S1A', 0), key=f"{key_prefix}1a")
        m['S1B'] = c2.number_input(f"S1 {m['B']['name']}", 0, 30, m.get('S1B', 0), key=f"{key_prefix}1b")
        m['S2A'] = c1.number_input(f"S2 {m['A']['name']}", 0, 30, m.get('S2A', 0), key=f"{key_prefix}2a")
        m['S2B'] = c2.number_input(f"S2 {m['B']['name']}", 0, 30, m.get('S2B', 0), key=f"{key_prefix}2b")
        
        set_a = (1 if m['S1A'] > m['S1B'] else 0) + (1 if m['S2A'] > m['S2B'] else 0)
        set_b = (1 if m['S1B'] > m['S1A'] else 0) + (1 if m['S2B'] > m['S2A'] else 0)
        
        if set_a == 1 and set_b == 1:
            m['S3A'] = c1.number_input(f"TIE {m['A']['name']}", 0, 20, m.get('S3A', 0), key=f"{key_prefix}3a")
            m['S3B'] = c2.number_input(f"TIE {m['B']['name']}", 0, 20, m.get('S3B', 0), key=f"{key_prefix}3b")
        else:
            m['S3A'], m['S3B'] = 0, 0
            
        m['Fatto'] = st.checkbox("Match Concluso", m.get('Fatto', False), key=f"{key_prefix}f")
        st.markdown("---")
        return m

# --- FASE SETUP E GIRONI (Invariate, vedi versioni precedenti) ---
if st.session_state['phase'] == "Setup":
    st.title("🏐 ZERO SKILLS CUP")
    t1, t2 = st.tabs(["Iscrizioni", "Cassa Storica"])
    with t1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            with st.form("isc"):
                un = st.toggle("Nome custom"); nc = st.text_input("Nome") if un else ""
                at1 = st.text_input("Atleta 1"); at2 = st.text_input("Atleta 2")
                q = st.number_input("Quota", 10); p = st.checkbox("Pagato")
                if st.form_submit_button("Iscrivi"):
                    n = nc if (un and nc) else f"{at1[:3]}-{at2[:3]}".upper()
                    st.session_state['teams'].append({"name":n,"p1":at1,"p2":at2,"quota":q,"pagato":p,"full":f"{n} ({at1}/{at2})"})
                    if at1 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(at1)
                    if at2 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(at2)
                    st.rerun()
        with c2:
            for i, t in enumerate(st.session_state['teams']):
                st.write(f"{'✅' if t['pagato'] else '❌'} {t['full']}")
            if len(st.session_state['teams']) >= 4 and st.button("🚀 AVVIA TORNEO"):
                st.session_state['matches'] = [{"A":st.session_state['teams'][i],"B":st.session_state['teams'][j],"S1A":0,"S1B":0,"S2A":0,"S2B":0,"S3A":0,"S3B":0,"Fatto":False} for i in range(len(st.session_state['teams'])) for j in range(i+1, len(st.session_state['teams']))]
                st.session_state['phase'] = "Gironi"; st.rerun()
    with t2: st.table(pd.DataFrame(st.session_state['storico_incassi']))

elif st.session_state['phase'] == "Gironi":
    st.title("🎾 FASE A GIRONI")
    for i, m in enumerate(st.session_state['matches']):
        st.session_state['matches'][i] = input_match(m, f"g{i}")
    
    # Calcolo Classifica...
    stats = {t['full']: {"P":0,"SV":0,"SP":0,"PF":0,"PS":0,"obj":t} for t in st.session_state['teams']}
    for m in st.session_state['matches']:
        if m['Fatto']:
            sa = (1 if m['S1A']>m['S1B'] else 0) + (1 if m['S2A']>m['S2B'] else 0) + (1 if m['S3A']>m['S3B'] and (m['S3A']+m['S3B']>0) else 0)
            sb = (1 if m['S1B']>m['S1A'] else 0) + (1 if m['S2B']>m['S2A'] else 0) + (1 if m['S3B']>m['S3A'] and (m['S3A']+m['S3B']>0) else 0)
            stats[m['A']['full']]['SV']+=sa; stats[m['A']['full']]['SP']+=sb
            stats[m['B']['full']]['SV']+=sb; stats[m['B']['full']]['SP']+=sa
            stats[m['A']['full']]['PF']+=(m['S1A']+m['S2A']+m['S3A']); stats[m['A']['full']]['PS']+=(m['S1B']+m['S2B']+m['S3B'])
            stats[m['B']['full']]['PF']+=(m['S1B']+m['S2B']+m['S3B']); stats[m['B']['full']]['PS'] += (m['S1A']+m['S2A']+m['S3A'])
            if sa > sb: stats[m['A']['full']]['P'] += 3
            else: stats[m['B']['full']]['P'] += 3

    df = pd.DataFrame.from_dict(stats, orient='index').reset_index().sort_values(["P","SV"], ascending=False)
    st.table(df[['index','P','SV','PF','PS']])
    if st.button("🏆 GENERA TABELLONE PLAYOFF"):
        top = [stats[n]['obj'] for n in df['index'][:4]]
        st.session_state['playoffs'] = [
            {"N":"SF 1 (1° vs 4°)","A":top[0],"B":top[3],"S1A":0,"S1B":0,"S2A":0,"S2B":0,"S3A":0,"S3B":0,"Fatto":False},
            {"N":"SF 2 (2° vs 3°)","A":top[1],"B":top[2],"S1A":0,"S1B":0,"S2A":0,"S2B":0,"S3A":0,"S3B":0,"Fatto":False}
        ]
        st.session_state['phase'] = "Playoff"; st.rerun()

# --- FASE PLAYOFF (FORMATO BRACKET) ---
elif st.session_state['phase'] == "Playoff":
    st.title("🔥 TABELLONE ELIMINATORIA")
    
    
    col_sf, col_spacer, col_f = st.columns([1, 0.2, 1])
    
    with col_sf:
        st.subheader("🛡️ Semifinali")
        for i in range(2):
            st.session_state['playoffs'][i] = input_match(st.session_state['playoffs'][i], f"p{i}")
            
        if all(p['Fatto'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
            if st.button("PROSSIMO TURNO: FINALI ➔"):
                def get_v(m): return m['A'] if (m['S1A']+m['S2A']+m['S3A']) > (m['S1B']+m['S2B']+m['S3B']) else m['B']
                def get_l(m): return m['B'] if (m['S1A']+m['S2A']+m['S3A']) > (m['S1B']+m['S2B']+m['S3B']) else m['A']
                st.session_state['playoffs'].append({"N":"🥇 FINALE 1° POSTO","A":get_v(st.session_state['playoffs'][0]),"B":get_v(st.session_state['playoffs'][1]),"S1A":0,"S1B":0,"S2A":0,"S2B":0,"S3A":0,"S3B":0,"Fatto":False})
                st.session_state['playoffs'].append({"N":"🥉 FINALE 3° POSTO","A":get_l(st.session_state['playoffs'][0]),"B":get_l(st.session_state['playoffs'][1]),"S1A":0,"S1B":0,"S2A":0,"S2B":0,"S3A":0,"S3B":0,"Fatto":False})
                st.rerun()

    with col_f:
        if len(st.session_state['playoffs'])
