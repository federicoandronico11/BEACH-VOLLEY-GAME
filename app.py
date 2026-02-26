import streamlit as st
import database, ui_components, random

st.set_page_config(page_title="Z-SKILLS CUP 26", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# --- SIDEBAR: LIVE RANKING & CARRIERA ---
with st.sidebar:
    st.markdown("<h2 style='color: #00ff85; font-family: Oswald;'>🏆 LIVE RANKING</h2>", unsafe_allow_html=True)
    if st.session_state.ranking_atleti:
        sorted_rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
        for i, (nome, punti) in enumerate(sorted_rank):
            with st.expander(f"{i+1}. {nome.upper()} - {punti} PT"):
                s = st.session_state.atleti_stats.get(nome, {})
                if s:
                    qp = round(s['pf'] / max(1, s['ps']), 3)
                    qs = round(s['sv'] / max(1, s['sp']), 2)
                    st.markdown(f"🏅 **MEDAGLIE:** {'🥇' * s['medaglie']}")
                    c1, c2 = st.columns(2); c1.metric("SET V/P", f"{s['sv']}/{s['sp']}"); c2.metric("Q. SET", qs)
                    c3, c4 = st.columns(2); c3.metric("PUNTI F/S", f"{s['pf']}/{s['ps']}"); c4.metric("Q. PUNTI", qp)
                    st.line_chart(s['history'], height=100)
    else: 
        st.info("Inizia un match per vedere il ranking")
    
    st.divider()
    if st.button("🏠 TORNA ALL'HUB"): 
        st.session_state.menu_attivo = "HUB"
        st.rerun()

# --- HUB PRINCIPALE ---
if st.session_state.menu_attivo == "HUB":
    st.markdown("<h1 style='text-align: center; color: #00ff85; font-family: Oswald; letter-spacing: 4px;'>ZERO SKILLS CUP 26</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="fc-tile"><h2>GESTIONE</h2><p>Iscrizioni & Setup</p></div>', unsafe_allow_html=True)
        if st.button("SETUP TORNEO", use_container_width=True): 
            st.session_state.menu_attivo = "SETUP"
            st.rerun()
    with c2:
        st.markdown('<div class="fc-tile"><h2>MATCH DAY</h2><p>Risultati Live</p></div>', unsafe_allow_html=True)
        if st.button("CAMPO LIVE", use_container_width=True): 
            st.session_state.menu_attivo = "LIVE"
            st.rerun()
    with c3:
        st.markdown('<div class="fc-tile"><h2>CLUB HOUSE</h2><p>Hall of Fame</p></div>', unsafe_allow_html=True)
        if st.button("RANKING TOTALE", use_container_width=True): 
            st.session_state.menu_attivo = "RANKING"
            st.rerun()

# --- SEZIONE SETUP ---
elif st.session_state.menu_attivo == "SETUP":
    st.markdown("<h2 style='color: #00ff85; font-family: Oswald;'>⚙️ CONFIGURAZIONE TORNEO</h2>", unsafe_allow_html=True)
    
    col_cfg, col_pay = st.columns([2,1])
    with col_cfg:
        st.session_state.settings['match_type'] = st.radio("FORMATO MATCH", ["Set Unico", "Best of 3"], horizontal=True, key="cfg_match_type")
        st.session_state.settings['punti_set'] = st.slider("PUNTI VITTORIA SET", 11, 30, st.session_state.settings['punti_set'], key="cfg_punti_set")
    with col_pay:
        incasso = sum(t['quota'] for t in st.session_state.teams if t['pagato'])
        st.metric("INCASSO LIVE", f"{incasso}€", f"{len(st.session_state.teams)} Team")

    st.divider()
    st.subheader("📝 ISCRIZIONE SQUADRA")
    
    with st.form("iscrizione_squadre_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            at1 = st.selectbox("Atleta 1 (Esistente)", [""] + st.session_state.db_atleti, key="sel_at1")
            at1_new = st.text_input("...o Nuovo Nome 1", key="txt_at1")
        with c2:
            at2 = st.selectbox("Atleta 2 (Esistente)", [""] + st.session_state.db_atleti, key="sel_at2")
            at2_new = st.text_input("...o Nuovo Nome 2", key="txt_at2")
        with c3:
            q_val = st.number_input("Quota €", 0, 100, 10, key="num_quota")
            q_on = st.toggle("Pagato", value=True, key="tgl_pagato")
            
        submit_team = st.form_submit_button("REGISTRA SQUADRA IN LISTA")
        
        if submit_team:
            p1 = at1_new if at1_new else at1
            p2 = at2_new if at2_new else at2
            if p1 and p2 and p1 != p2:
                new_team = {
                    "name": f"{p1[:3]}-{p2[:3]}".upper(),
                    "p1": p1, "p2": p2, "quota": q_val, "pagato": q_on, "is_bye": False
                }
                st.session_state.teams.append(new_team)
                for p in [p1, p2]:
                    if p not in st.session_state.db_atleti: st.session_state.db_atleti.append(p)
                st.rerun()
            else:
                st.error("Inserisci nomi validi e diversi!")

    if len(st.session_state.teams) >= 2:
        st.write("---")
        if st.button("🚀 GENERA TABELLONE PRO (INC. BYE)", type="primary", use_container_width=True):
            teams_list = st.session_state.teams.copy()
            n = len(teams_list)
            prossima_potenza_2 = 2**(n - 1).bit_length() if n > 2 else 4
            num_bye = prossima_potenza_2 - n
            
            for i in range(num_bye):
                teams_list.append({
                    "name": "BYE (FREE WIN)", "p1": "SISTEMA", "p2": "SISTEMA", 
                    "is_bye": True, "quota": 0, "pagato": True
                })
            
            random.shuffle(teams_list)
            st.session_state.matches = []
            pts_win = st.session_state.settings['punti_set']
            
            for i in range(0, len(teams_list), 2):
                t_a, t_b = teams_list[i], teams_list[i+1]
                m = {"A": t_a, "B": t_b, "S1A": 0, "S1B": 0, "Fatto": False, "Note": ""}
                if t_a.get("is_bye"): m.update({"S1B": pts_win, "Fatto": True, "Note": "Vittoria a tavolino"})
                elif t_b.get("is_bye"): m.update({"S1A": pts_win, "Fatto": True, "Note": "Vittoria a tavolino"})
                st.session_state.matches.append(m)
            
            st.session_state.phase = "Gironi"
            st.session_state.menu_attivo = "LIVE"
            st.rerun()

# --- SEZIONE LIVE ---
elif st.session_state.menu_attivo == "LIVE":
    if st.session_state.phase == "Gironi":
        st.subheader("📺 Fase a Gironi")
        for i, m in enumerate(st.session_state.matches):
            st.markdown(f'<div class="broadcast-card"><div class="team-red">{m["A"]["name"]}</div><div class="score-box">{m["S1A"]}-{m["S1B"]}</div><div class="team-blue">{m["B"]["name"]}</div></div>', unsafe_allow_html=True)
            
            if not m['Fatto']:
                c1, c2, c3 = st.columns([1,1,1])
                m['S1A'] = c1.number_input("Punti A", 0, 45, m['S1A'], key=f"s1a{i}")
                m['S1B'] = c2.number_input("Punti B", 0, 45, m['S1B'], key=f"s1b{i}")
                
                if c3.button("CONFERMA", key=f"btn{i}"):
                    m['Fatto'] = True
                    if not m['A'].get('is_bye'):
                        database.aggiorna_carriera(m['A'], m['S1A'], m['S1B'], m['S1A'] > m['S1B'], 1 if m['S1A']>m['S1B'] else 0, 1 if m['S1B']>m['S1A'] else 0)
                    if not m['B'].get('is_bye'):
                        database.aggiorna_carriera(m['B'], m['S1B'], m['S1A'], m['S1B'] > m['S1A'], 1 if m['S1B']>m['S1A'] else 0, 1 if m['S1A']>m['S1B'] else 0)
                    st.rerun()
            else:
                st.caption(f"Match Concluso. {m.get('Note', '')}")
        
        if all(m['Fatto'] for m in st.session_state.matches):
            if st.button("🏆 PASSA AI PLAYOFF"):
                vincitori = []
                for m in st.session_state.matches:
                    vincitori.append(m['A'] if m['S1A'] > m['S1B'] else m['B'])
                st.session_state.playoffs = [{"A": vincitori[0], "B": vincitori[1], "S1A":0, "S1B":0, "Fatto":False, "N":"FINALE"}]
                st.session_state.phase = "Eliminazione"
                st.rerun()

    elif st.session_state.phase == "Eliminazione":
        st.subheader("🔥 Fase Finale")
        for i, p in enumerate(st.session_state.playoffs):
            st.markdown(f"**{p['N']}**")
            st.markdown(f'<div class="broadcast-card"><div>{p["A"]["name"]}</div><div class="score-box">{p["S1A"]}-{p["S1B"]}</div><div>{p["B"]["name"]}</div></div>', unsafe_allow_html=True)
            if not p['Fatto']:
                c1, c2, c3 = st.columns([1,1,1])
                p['S1A'] = c1.number_input("Punti A", 0, 45, p['S1A'], key=f"pa{i}")
                p['S1B'] = c2.number_input("Punti B", 0, 45, p['S1B'], key=f"pb{i}")
                if c3.button("CONFERMA", key=f"pbtn{i}"):
                    p['Fatto'] = True
                    database.aggiorna_carriera(p['A'], p['S1A'], p['S1B'], p['S1A'] > p['S1B'], 1 if p['S1A']>p['S1B'] else 0, 1 if p['S1B']>p['S1A'] else 0)
                    database.aggiorna_carriera(p['B'], p['S1B'], p['S1A'], p['S1B'] > p['S1A'], 1 if p['S1B']>p['S1A'] else 0, 1 if p['S1A']>p['S1B'] else 0)
                    st.rerun()
            
            if p['Fatto'] and p['N'] == "FINALE":
                win = p['A'] if p['S1A'] > p['S1B'] else p['B']
                st.balloons()
                st.markdown(f'<div class="winner-reveal"><h1>🏆 CAMPIONI 🏆</h1><h2>{win["name"]}</h2></div>', unsafe_allow_html=True)
                if st.button("💾 ARCHIVIA E CHIUDI"):
                    for a in [win['p1'], win['p2']]:
                        if a in st.session_state.atleti_stats: st.session_state.atleti_stats[a]['medaglie'] += 1
                    st.session_state.phase = "Setup"; st.session_state.teams = []; st.session_state.menu_attivo = "HUB"
                    st.rerun()

# --- SEZIONE RANKING ---
elif st.session_state.menu_attivo == "RANKING":
    st.markdown("<h1 style='text-align: center; color: #00ff85; font-family: Oswald;'>🏆 CLUB HOUSE - HALL OF FAME</h1>", unsafe_allow_html=True)
    
    rank_list = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
    
    # PODIO MODERNO (Solo se ci sono almeno 3 atleti)
    if len(rank_list) >= 3:
        p1, p2, p3 = rank_list[0], rank_list[1], rank_list[2]
        st.markdown(f"""
        <div class="podium-container">
            <div class="podium-step second">
                <div class="podium-rank">2</div>
                <div class="podium-name">{p2[0]}</div>
                <div style="color:#00ff85">{p2[1]} PT</div>
            </div>
            <div class="podium-step first">
                <div class="podium-rank">1</div>
                <div class="podium-name">{p1[0]}</div>
                <div style="color:#00ff85">{p1[1]} PT</div>
            </div>
            <div class="podium-step third">
                <div class="podium-rank">3</div>
                <div class="podium-name">{p3[0]}</div>
                <div style="color:#00ff85">{p3[1]} PT</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("### 👥 CLASSIFICA ATLETI (Seleziona un nome per i dettagli)")
    
    # Visualizzazione Tabellare Interattiva
    for i, (nome, punti) in enumerate(rank_list):
        if st.button(f"{i+1}º | {nome.upper()} — {punti} PT", key=f"rank_btn_{nome}", use_container_width=True):
            st.session_state.atleta_selezionato = nome

    # SCHEDA CARRIERA (Mostrata quando si clicca un atleta)
    if 'atleta_selezionato' in st.session_state:
        nome_sel = st.session_state.atleta_selezionato
        s = st.session_state.atleti_stats.get(nome_sel, {})
        
        st.markdown("---")
        st.subheader(f"👤 SCHEDA ATLETA: {nome_sel.upper()}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PUNTI TOTALI", st.session_state.ranking_atleti[nome_sel])
        c2.metric("MEDAGLIE 🥇", s.get('medaglie', 0))
        c3.metric("SET VINTI", s.get('sv', 0))
        c4.metric("SET PERSI", s.get('sp', 0))
        
        st.markdown("#### 📜 ULTIME GARE DISPUTATE")
        logs = s.get('match_logs', [])
        if logs:
            for log in reversed(logs):
                col_res, col_score = st.columns([1,4])
                res_color = "#00ff85" if log['esito'] == "Vittoria" else "#ff4b4b"
                col_res.markdown(f"<span style='color:{res_color}; font-weight:bold;'>{log['esito']}</span>", unsafe_allow_html=True)
                col_score.write(f"Risultato: {log['punteggio']} contro {log['avversario']}")
        else:
            st.info("Nessun match registrato per questo atleta.")
            
        if st.button("Chiudi Scheda Atleta"):
            del st.session_state.atleta_selezionato
            st.rerun()
