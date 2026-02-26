import streamlit as st
import database, ui_components, simulator, pandas as pd

st.set_page_config(page_title="Z-Skills Pro Tournament", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🏆 PRO TOURNEY")
    nav = st.radio("SPOSTATI IN:", ["⚙️ SETUP & ISCRIVITI", "📺 TABELLONE LIVE", "📊 RANKING & CARRIERA"])
    st.divider()
    if st.button("🔄 RESET COMPLETO", type="secondary"):
        st.session_state.clear()
        st.rerun()

# --- FASE 1: SETUP E ISCRIZIONE ---
if nav == "⚙️ SETUP & ISCRIVITI":
    st.header("Configurazione Torneo")
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        st.session_state.match_type = st.radio("Formato Partita", ["Set Unico", "Best of 3"])
        st.session_state.settings['punti_set'] = st.number_input("Punti Set Standard", 5, 30, 21)
    with col_cfg2:
        st.session_state.settings['formato'] = st.selectbox("Tabellone", ["Gironi + Playoff", "Doppia Eliminazione"])
        st.metric("SQUADRE ISCRITTE", len(st.session_state.teams))

    st.divider()
    st.subheader("📝 Iscrivi una Squadra")
    with st.form("form_iscrizione", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        # Logica Duale: Scelta o Scrittura
        at1_ex = c1.selectbox("Atleta 1 (Esistente)", [""] + st.session_state.db_atleti)
        at1_new = c1.text_input("Atleta 1 (Nuovo)")
        at2_ex = c2.selectbox("Atleta 2 (Esistente)", [""] + st.session_state.db_atleti)
        at2_new = c2.text_input("Atleta 2 (Nuovo)")
        quota = c3.number_input("Quota €", 10)
        pagato = c3.checkbox("Pagato", value=True)
        
        if st.form_submit_button("CONFERMA ISCRIZIONE"):
            p1 = at1_new if at1_new else at1_ex
            p2 = at2_new if at2_new else at2_ex
            if p1 and p2:
                name = f"{p1[:3]}-{p2[:3]}".upper()
                st.session_state.teams.append({"name": name, "p1": p1, "p2": p2, "quota": quota, "pagato": pagato})
                for p in [p1, p2]:
                    if p not in st.session_state.db_atleti: st.session_state.db_atleti.append(p)
                st.rerun()

    if st.session_state.teams:
        st.write("### Team Iscritti:")
        for t in st.session_state.teams: st.write(f"✅ {t['name']} ({t['p1']} / {t['p2']})")
        
        if st.button("🚀 GENERA E INIZIA TORNEO", type="primary", use_container_width=True):
            # Generazione calendario round-robin
            st.session_state.matches = []
            for i in range(len(st.session_state.teams)):
                for j in range(i+1, len(st.session_state.teams)):
                    st.session_state.matches.append({
                        "A": st.session_state.teams[i], "B": st.session_state.teams[j],
                        "S1A":0, "S1B":0, "S2A":0, "S2B":0, "S3A":0, "S3B":0, "Fatto": False
                    })
            st.session_state.phase = "Gironi"
            st.success("Tabellone Generato! Vai alla sezione LIVE.")

# --- FASE 2: TABELLONE LIVE (LOOK DAZN) ---
elif nav == "📺 TABELLONE LIVE":
    if not st.session_state.get('matches'):
        st.warning("⚠️ Genera il torneo nel Setup prima di accedere qui.")
    else:
        st.header("📺 Diretta Tabellone")
        with st.expander("🎲 SIMULATORE AVANZATO"):
            to_rank = st.toggle("Trasferisci risultati simulati al Ranking", value=False)
            if st.button("ESEGUI SIMULAZIONE RANDOM"):
                simulator.run_simulation(to_rank)
                st.rerun()

        for i, m in enumerate(st.session_state.matches):
            st.markdown(f"""
            <div class="broadcast-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="team-name-red">{m['A']['name']}</div>
                    <div class="score-center">{m['S1A']} - {m['S1B']}</div>
                    <div class="team-name-blue">{m['B']['name']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4, c5 = st.columns([1,1,1,1,2])
            m['S1A'] = c1.number_input("S1 A", 0, 45, m['S1A'], key=f"s1a{i}")
            m['S1B'] = c2.number_input("S1 B", 0, 45, m['S1B'], key=f"s1b{i}")
            
            if st.session_state.match_type == "Best of 3":
                m['S2A'] = c3.number_input("S2 A", 0, 45, m['S2A'], key=f"s2a{i}")
                m['S2B'] = c4.number_input("S2 B", 0, 45, m['S2B'], key=f"s2b{i}")
                # Logica automatica Tie-break (mostra solo se necessario)
                if (m['S1A'] > m['S1B'] and m['S2B'] > m['S2A']) or (m['S1B'] > m['S1A'] and m['S2A'] > m['S2B']):
                    m['S3A'] = st.number_input("S3 A", 0, 45, m.get('S3A',0), key=f"s3a{i}")
                    m['S3B'] = st.number_input("S3 B", 0, 45, m.get('S3B',0), key=f"s3b{i}")

            if c5.button("✅ CONFERMA", key=f"btn{i}"):
                m['Fatto'] = True
                database.registra_risultato_completo(m)
                st.toast(f"Risultato {m['A']['name']} vs {m['B']['name']} salvato!")
                # Sotto il ciclo dei match dei gironi
    if st.session_state.phase == "Gironi":
        if all(m['Fatto'] for m in st.session_state.matches):
            st.divider()
            if st.button("🏆 CALCOLA CLASSIFICA E GENERA PLAYOFF", type="primary", use_container_width=True):
                # Calcolo punti: 3 per vittoria, 0 sconfitta + Quoziente Punti
                classifica = []
                for t in st.session_state.teams:
                    vittorie = sum(1 for m in st.session_state.matches if m['Fatto'] and 
                                 ((m['A']['name'] == t['name'] and m['S1A'] > m['S1B']) or 
                                  (m['B']['name'] == t['name'] and m['S1B'] > m['S1A'])))
                    pf = sum(m['S1A'] if m['A']['name'] == t['name'] else m['S1B'] for m in st.session_state.matches if m['Fatto'])
                    ps = sum(m['S1B'] if m['A']['name'] == t['name'] else m['S1A'] for m in st.session_state.matches if m['Fatto'])
                    classifica.append({"team": t, "v": vittorie, "diff": pf - ps})
                
                # Ordina per vittorie e poi differenza punti
                classifica = sorted(classifica, key=lambda x: (x['v'], x['diff']), reverse=True)
                
                # Prendi i primi 4 per le Semifinali
                st.session_state.playoffs = [
                    {"N": "SF1", "A": classifica[0]['team'], "B": classifica[3]['team'], "Fatto": False, "S1A":0, "S1B":0},
                    {"N": "SF2", "A": classifica[1]['team'], "B": classifica[2]['team'], "Fatto": False, "S1A":0, "S1B":0}
                ]
                st.session_state.phase = "Playoff"
                st.rerun()

#### B. Logica Playoff e Finale (da aggiungere in coda a Live)
    elif st.session_state.phase == "Playoff":
        st.subheader("🔥 FASE AD ELIMINAZIONE DIRETTA")
        
        # Visualizza Semifinali
        for i, p in enumerate(st.session_state.playoffs[:2]):
            st.markdown(f"**SEMIFINALE {i+1}**")
            # Usa lo stesso widget dei match broadcast qui... (omesso per brevità)
            # Se entrambe le SF sono 'Fatto', genera la Finale
            
        if all(p['Fatto'] for p in st.session_state.playoffs[:2]) and len(st.session_state.playoffs) == 2:
            if st.button("🏁 GENERA FINALISSIMA"):
                w1 = st.session_state.playoffs[0]['A'] if st.session_state.playoffs[0]['S1A'] > st.session_state.playoffs[0]['S1B'] else st.session_state.playoffs[0]['B']
                w2 = st.session_state.playoffs[1]['A'] if st.session_state.playoffs[1]['S1A'] > st.session_state.playoffs[1]['S1B'] else st.session_state.playoffs[1]['B']
                st.session_state.playoffs.append({"N": "FINALE", "A": w1, "B": w2, "Fatto": False, "S1A":0, "S1B":0})
                st.rerun()

        # Visualizza Finale
        if len(st.session_state.playoffs) > 2:
            st.divider()
            st.error("🏆 FINALISSIMA")
            m_f = st.session_state.playoffs[2]
            # Widget input punti per m_f...
            
            if m_f['Fatto']:
                vincitore = m_f['A'] if m_f['S1A'] > m_f['S1B'] else m_f['B']
                st.balloons() # Animazione Streamlit
                st.markdown(f"""
                <div style="text-align:center; padding:50px; background:linear-gradient(45deg, #ffd700, #ff8c00); border-radius:15px;">
                    <h1 style="color:white; font-size:4rem;">🏆 CAMPIONI 🏆</h1>
                    <h2 style="color:white; font-size:2.5rem;">{vincitore['name']}</h2>
                    <p style="color:white;">{vincitore['p1']} & {vincitore['p2']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("💾 ARCHIVIA E AGGIORNA RANKING"):
                    # Crea lista nomi ordinata per i punti ranking
                    nomi_ordinati = [vincitore['name']] # (Logica per aggiungere gli altri posizionamenti)
                    database.archivia_torneo_completo(vincitore['name'], nomi_ordinati)
                    st.session_state.phase = "Setup"
                    st.success("Dati inviati alla Hall of Fame!")
                    st.rerun()

# --- FASE 3: RANKING & CARRIERA ---
elif nav == "📊 RANKING & CARRIERA":
    st.title("🏆 Ranking & Hall of Fame")
    
    # Calcolo classifica ordinata per vittorie e poi quoziente punti
    stats = st.session_state.atleti_stats
    if not stats:
        st.info("Nessun dato disponibile. Concludi i primi match!")
    else:
        rank = sorted(stats.items(), key=lambda x: (x[1]['v'], x[1]['pf']-x[1]['ps']), reverse=True)
        
        # PODIO
        st.markdown('<div class="podio-wrap">', unsafe_allow_html=True)
        if len(rank) > 1: st.markdown(f'<div class="podio-item" style="background:#c0c0c0; height:130px;">🥈<br>{rank[1][0]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="podio-item" style="background:#ffd700; height:180px;">🥇<br>{rank[0][0]}</div>', unsafe_allow_html=True)
        if len(rank) > 2: st.markdown(f'<div class="podio-item" style="background:#cd7f32; height:90px;">🥉<br>{rank[2][0]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # CARRIERA ATLETA
        st.subheader("Dettaglio Carriera Atleti")
        for name, data in rank:
            with st.expander(f"👤 {name} | Record: {data['v']}V - {data['p']}P"):
                col1, col2, col3 = st.columns(3)
                qp = round(data['pf']/max(1,data['ps']), 3)
                qs = round(data['sv']/max(1,data['sp']), 2)
                col1.metric("Quoziente Punti", qp)
                col2.metric("Quoziente Set", qs)
                col3.metric("Punti Totali", data['pf'])
                
                if data['history']:
                    st.write("Andamento (Differenziale Punti):")
                    st.line_chart(data['history'])
