import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_session, assegna_punti_finali, registra_incasso_torneo, aggiorna_database_storico, chiudi_torneo_atleta
from ui_components import load_styles, display_sidebar

st.set_page_config(page_title="Zero Skills Cup Pro", layout="wide")
init_session()
load_styles()
display_sidebar()

# --- WIDGET SEGNAPUNTI ---
def show_digital_scoreboard():
    st.markdown("<div class='scoreboard-box'>", unsafe_allow_html=True)
    st.subheader("📟 SEGNAPUNTI DIGITALE")
    if 'live_pt' not in st.session_state: st.session_state.live_pt = {"A":0, "B":0}
    
    c1, c2, c3 = st.columns([2,1,2])
    with c1:
        team_a = st.selectbox("Squadra A", [t['name'] for t in st.session_state['teams']])
        if st.button("➕ PUNTO A"): st.session_state.live_pt["A"] += 1; st.rerun()
    with c2:
        st.markdown(f"<div class='score-display'>{st.session_state.live_pt['A']} - {st.session_state.live_pt['B']}</div>", unsafe_allow_html=True)
        if st.button("🔄 RESET"): st.session_state.live_pt = {"A":0, "B":0}; st.rerun()
    with c3:
        team_b = st.selectbox("Squadra B", [t['name'] for t in st.session_state['teams']])
        if st.button("➕ PUNTO B"): st.session_state.live_pt["B"] += 1; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- FUNZIONE MATCH ---
def render_match_input(m, key):
    with st.expander(f"📌 {m['N']}: {m['A']['name']} vs {m['B']['name']}"):
        if m['B']['name'] == "BYE":
            st.info("Partita vinta a tavolino (BYE)")
            m['S1A'], m['S1B'], m['Fatto'] = 21, 0, True
            return m
        
        c1, c2 = st.columns(2)
        m['S1A'] = c1.number_input(f"Set 1 - {m['A']['name']}", 0, 30, m.get('S1A',0), key=f"{key}1a")
        m['S1B'] = c2.number_input(f"Set 1 - {m['B']['name']}", 0, 30, m.get('S1B',0), key=f"{key}1b")
        
        if st.session_state['match_type'] == "Best of 3":
            m['S2A'] = c1.number_input(f"Set 2 - {m['A']['name']}", 0, 30, m.get('S2A',0), key=f"{key}2a")
            m['S2B'] = c2.number_input(f"Set 2 - {m['B']['name']}", 0, 30, m.get('S2B',0), key=f"{key}2b")
            # Tie-break se necessario
            if (m['S1A']>m['S1B'] and m['S2B']>m['S2A']) or (m['S1B']>m['S1A'] and m['S2A']>m['S2B']):
                m['S3A'] = c1.number_input(f"TIE-BREAK - {m['A']['name']}", 0, 30, m.get('S3A',0), key=f"{key}3a")
                m['S3B'] = c2.number_input(f"TIE-BREAK - {m['B']['name']}", 0, 30, m.get('S3B',0), key=f"{key}3b")
        
        m['Fatto'] = st.checkbox("Conferma Risultato", m.get('Fatto', False), key=f"{key}f")
        return m

# --- FASE SETUP ---
if st.session_state['phase'] == "Setup":
    st.title("🏐 ZERO SKILLS CUP")
    st.session_state['match_type'] = st.radio("Formato Partita", ["Set Unico", "Best of 3"], horizontal=True)
    
    with st.form("isc_form", clear_on_submit=True):
        a1 = st.text_input("Atleta 1"); a2 = st.text_input("Atleta 2")
        if st.form_submit_button("Aggiungi Squadra"):
            if a1 and a2:
                n = f"{a1[:3]}-{a2[:3]}".upper()
                st.session_state['teams'].append({"name":n, "p1":a1, "p2":a2, "full":f"{n} ({a1}/{a2})"})
                if a1 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a1)
                if a2 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a2)
                st.rerun()

    for t in st.session_state['teams']: st.write(f"✔ {t['full']}")
    
    if len(st.session_state['teams']) >= 3 and st.button("🚀 INIZIA TORNEO"):
        lt = st.session_state['teams'].copy()
        if len(lt) % 2 != 0: lt.append({"name":"BYE", "p1":"N/A", "p2":"N/A"})
        st.session_state['matches'] = [{"N": f"Match {i+1}", "A":lt[i], "B":lt[j], "Fatto":False} for i in range(len(lt)) for j in range(i+1, len(lt))]
        st.session_state['phase'] = "Gironi"; st.rerun()

# --- FASE GIRONI ---
elif st.session_state['phase'] == "Gironi":
    show_digital_scoreboard()
    st.title("🎾 GIRONI")
    for i, m in enumerate(st.session_state['matches']):
        st.session_state['matches'][i] = render_match_input(m, f"g{i}")
    
    # Classifica
    stats = {t['full']: {"P":0,"SV":0,"SP":0,"PF":0,"PS":0,"obj":t} for t in st.session_state['teams']}
    for m in st.session_state['matches']:
        if m['Fatto']:
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
    
    if st.button("🏆 VAI AL TABELLONE"):
        top = [stats[n]['obj'] for n in df['index'][:4]]
        st.session_state['playoffs'] = [
            {"N":"SF1 (1° vs 4°)","A":top[0],"B":top[3],"Fatto":False},
            {"N":"SF2 (2° vs 3°)","A":top[1],"B":top[2],"Fatto":False}
        ]
        st.session_state['phase'] = "Playoff"; st.rerun()

# --- FASE PLAYOFF (BRACKET) ---
elif st.session_state['phase'] == "Playoff":
    show_digital_scoreboard()
    st.title("🔥 PLAYOFF BRACKET")
    
    

    c_sf, c_f = st.columns(2)
    with c_sf:
        st.subheader("🛡️ Semifinali")
        for i in range(2):
            st.session_state['playoffs'][i] = render_match_input(st.session_state['playoffs'][i], f"p{i}")
        
        if all(p['Fatto'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
            if st.button("Genera Finali ➔"):
                def win(m): return m['A'] if (m['S1A']+m.get('S2A',0)+m.get('S3A',0)) > (m['S1B']+m.get('S2B',0)+m.get('S3B',0)) else m['B']
                def los(m): return m['B'] if (m['S1A']+m.get('S2A',0)+m.get('S3A',0)) > (m['S1B']+m.get('S2B',0)+m.get('S3B',0)) else m['A']
                st.session_state['playoffs'].append({"N":"🥇 FINALE 1°","A":win(st.session_state['playoffs'][0]),"B":win(st.session_state['playoffs'][1]),"Fatto":False})
                st.session_state['playoffs'].append({"N":"🥉 FINALE 3°","A":los(st.session_state['playoffs'][0]),"B":los(st.session_state['playoffs'][1]),"Fatto":False})
                st.rerun()

    with c_f:
        if len(st.session_state['playoffs']) > 2:
            st.subheader("🏆 Finali")
            for i in range(2, 4):
                st.session_state['playoffs'][i] = render_match_input(st.session_state['playoffs'][i], f"f{i}")
            
            if all(f['Fatto'] for f in st.session_state['playoffs'][2:]):
                if st.button("🏁 CONCLUSIONE E PROCLAMAZIONE"):
                    # Salvataggio Dati
                    registra_incasso_torneo(st.session_state['teams'])
                    assegna_punti_finali(st.session_state['teams'])
                    
                    # Logica Medaglie e Statistiche (Tutti i match)
                    tutti = st.session_state['matches'] + st.session_state['playoffs']
                    for m in tutti:
                        if m['Fatto']:
                            for a, p1, p2, v1, v2 in [(m['A']['p1'], m['S1A']+m.get('S2A',0)+m.get('S3A',0), m['S1B']+m.get('S2B',0)+m.get('S3B',0), (1 if m['S1A']>m['S1B'] else 0), (1 if m['S1B']>m['S1A'] else 0))]: # Esempio per atleta 1
                                aggiorna_database_storico(a, p1, p2, v1, v2, 0, 0)
                    
                    f1 = st.session_state['playoffs'][2]
                    st.session_state['winner'] = f1['A']['name'] if (f1['S1A']>f1['S1B']) else f1['B']['name']
                    st.session_state['albo_oro'].append(f"🏆 {st.session_state['winner']} ({datetime.now().strftime('%d/%m')})")
                    st.session_state['phase'] = "Vittoria"; st.rerun()

elif st.session_state['phase'] == "Vittoria":
    st.markdown(f"""
    <div class='winner-card'>
        <h1>🥇 VINCITORI 🥇</h1>
        <h1 style='font-size: 80px;'>{st.session_state.get('winner', 'CAMPIONI')}</h1>
        <p>Il torneo è stato archiviato correttamente nel database.</p>
    </div>
    """, unsafe_allow_html=True)
    st.balloons()
    if st.button("NUOVO TORNEO"):
        st.session_state['teams'] = []; st.session_state['phase'] = "Setup"; st.rerun()
