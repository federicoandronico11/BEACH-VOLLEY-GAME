elif st.session_state.menu_attivo == "SETUP":
    st.markdown("<h2 style='color: #00ff85; font-family: Oswald;'>⚙️ TORNEO CONFIG</h2>", unsafe_allow_html=True)
    
    # --- RIGA 1: IMPOSTAZIONI TECNICHE ---
    col_settings, col_stats = st.columns([2, 1])
    
    with col_settings:
        with st.container():
            st.markdown('<div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border: 1px solid #00ff85;">', unsafe_allow_html=True)
            
            # 1. Scelta Tabellone
            st.session_state.settings['formato'] = st.radio(
                "TIPO TABELLONE", 
                ["Gironi + Eliminazione", "Doppia Eliminazione"], 
                horizontal=True
            )
            
            # 2. Scelta Set
            st.session_state.settings['match_type'] = st.radio(
                "FORMATO MATCH", 
                ["Set Unico", "Al meglio dei 3"], 
                horizontal=True
            )
            
            # 3. Punteggio Massimo
            st.session_state.settings['punti_set'] = st.select_slider(
                "PUNTEGGIO MASSIMO SET", 
                options=[11, 15, 21, 25, 30], 
                value=21
            )
            st.markdown('</div>', unsafe_allow_html=True)

    with col_stats:
        # Counter Live FC Style
        incasso_tot = sum(t['quota'] for t in st.session_state.teams if t['pagato'])
        st.markdown(f"""
            <div style="background: #00ff85; color: #000; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="margin:0;">SQUADRE ISCRITTE</h3>
                <h1 style="margin:0; font-size: 3rem;">{len(st.session_state.teams)}</h1>
                <hr style="border-color: #000;">
                <h4 style="margin:0;">INCASSO: {incasso_tot}€</h4>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- RIGA 2: ISCRIZIONE SQUADRE ---
    st.subheader("📝 REGISTRAZIONE TEAM")
    with st.form("fc_iscrizione", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        
        # Atleta 1: Cerca o Nuovo
        at1 = c1.selectbox("Seleziona Atleta 1", [""] + st.session_state.db_atleti, help="Cerca nel database")
        at1_n = c1.text_input("...o scrivi Nuovo Nome 1")
        
        # Atleta 2: Cerca o Nuovo
        at2 = c2.selectbox("Seleziona Atleta 2", [""] + st.session_state.db_atleti)
        at2_new = c2.text_input("...o scrivi Nuovo Nome 2")
        
        # Gestione Quota
        quota_on = c3.toggle("Quota Pagata", value=True)
        quota_val = c3.number_input("Importo €", 0, 100, 10)
        
        if st.form_submit_button("CONFERMA E AGGIUNGI TEAM"):
            p1 = at1_n if at1_n else at1
            p2 = at2_new if at2_new else at2
            
            if p1 and p2:
                # Creazione Nome Squadra Auto
                t_name = f"{p1[:3]}-{p2[:3]}".upper()
                st.session_state.teams.append({
                    "name": t_name, "p1": p1, "p2": p2, 
                    "quota": quota_val, "pagato": quota_on
                })
                # Aggiorna database atleti persistente
                for p in [p1, p2]:
                    if p not in st.session_state.db_atleti: st.session_state.db_atleti.append(p)
                st.rerun()
            else:
                st.error("Inserisci entrambi gli atleti!")

    # --- TASTO START ---
    if len(st.session_state.teams) >= 2:
        st.write("---")
        if st.button("🚀 GENERA TABELLONE E INIZIA MATCH DAY", type="primary", use_container_width=True):
            # Logica Calendario (Round Robin per gironi)
            st.session_state.matches = []
            for i in range(len(st.session_state.teams)):
                for j in range(i+1, len(st.session_state.teams)):
                    st.session_state.matches.append({
                        "A": st.session_state.teams[i], 
                        "B": st.session_state.teams[j],
                        "S1A": 0, "S1B": 0, 
                        "S2A": 0, "S2B": 0, 
                        "S3A": 0, "S3B": 0,
                        "Fatto": False
                    })
            st.session_state.phase = "Gironi"
            st.session_state.menu_attivo = "LIVE"
            st.rerun()

    if st.button("⬅️ RITORNA ALL'HUB"):
        st.session_state.menu_attivo = "HUB"
        st.rerun()
