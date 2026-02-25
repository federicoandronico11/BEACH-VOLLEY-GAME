with col1:
        st.subheader("Iscrizione Rapida")
        with st.form("iscrizione", clear_on_submit=True):
            # RIGA SQUADRA
            st.write("**Squadra**")
            c_t1, c_t2 = st.columns([1, 1])
            t_name = c_t1.selectbox("Esistente", ["-"] + st.session_state['db_teams'], label_visibility="collapsed")
            t_new = c_t2.text_input("Nuova Squadra", placeholder="Nome nuova squadra", label_visibility="collapsed")
            team_final = t_new if t_new else t_name

            # RIGA ATLETA 1
            st.write("**Atleta 1**")
            c_a1, c_a2 = st.columns([1, 1])
            p1_sel = c_a1.selectbox("Esistente 1", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p1_new = c_a2.text_input("Nuovo Atleta 1", placeholder="Nome e Cognome", label_visibility="collapsed")
            p1_final = p1_new if p1_new else p1_sel

            # RIGA ATLETA 2
            st.write("**Atleta 2**")
            c_b1, c_b2 = st.columns([1, 1])
            p2_sel = c_b1.selectbox("Esistente 2", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p2_new = c_b2.text_input("Nuovo Atleta 2", placeholder="Nome e Cognome", label_visibility="collapsed")
            p2_final = p2_new if p2_new else p2_sel

            # QUOTA E INVIO
            paid = st.checkbox("Quota pagata (€)")
            
            if st.form_submit_button("CONFERMA ISCRIZIONE", use_container_width=True):
                if team_final != "-" and p1_final != "-" and p2_final != "-":
                    st.session_state['teams'].append({
                        "full": f"{team_final} ({p1_final}/{p2_final})", 
                        "name": team_final, "p1": p1_final, "p2": p2_final, "paid": paid
                    })
                    # Aggiorna DB
                    if team_final not in st.session_state['db_teams']: st.session_state['db_teams'].append(team_final)
                    for p in [p1_final, p2_final]:
                        if p not in st.session_state['db_atleti']: 
                            st.session_state['db_atleti'].append(p)
                        if p not in st.session_state['ranking_atleti']:
                            st.session_state['ranking_atleti'][p] = 0
                    st.success(f"Iscritto: {team_final}")
                    st.rerun()
                else:
                    st.error("Mancano dei dati!")
