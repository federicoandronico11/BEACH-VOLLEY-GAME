import streamlit as st
import pandas as pd
from database import init_session
from ui_components import load_styles, display_sidebar_ranking

# 1. INIZIALIZZAZIONE AMBIENTE
# Impostiamo la pagina e carichiamo i moduli esterni confermati
st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar_ranking()

# 2. TITOLO E COUNTER DINAMICO
st.title("🏐 ZERO SKILLS CUP")

# 3. LOGICA DELLE FASI
if st.session_state['phase'] == "Setup":
    # Counter che legge in tempo reale la lunghezza della lista team
    numero_iscritti = len(st.session_state['teams'])
    st.markdown(f'''
        <div class="mega-counter">
            <div class="counter-val">{numero_iscritti}</div>
            <div style="color:#9370DB; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">Squadre Iscritte</div>
        </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Iscrizione Rapida")
        with st.form("form_iscrizione", clear_on_submit=True):
            # RIGA SQUADRA
            st.write("**Squadra**")
            ct1, ct2 = st.columns(2)
            t_name = ct1.selectbox("Seleziona Team", ["-"] + st.session_state['db_teams'], label_visibility="collapsed")
            t_new = ct2.text_input("Nuovo Team", placeholder="Nome nuova squadra", label_visibility="collapsed")
            team_final = t_new if t_new != "" else t_name

            # RIGA ATLETA 1
            st.write("**Atleta 1**")
            ca1, ca2 = st.columns(2)
            p1_sel = ca1.selectbox("Atleta 1 Esistente", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p1_new = ca2.text_input("Nuovo Atleta 1", placeholder="Nome e Cognome", label_visibility="collapsed")
            p1_final = p1_new if p1_new != "" else p1_sel

            # RIGA ATLETA 2
            st.write("**Atleta 2**")
            cb1, cb2 = st.columns(2)
            p2_sel = cb1.selectbox("Atleta 2 Esistente", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
            p2_new = cb2.text_input("Nuovo Atleta 2", placeholder="Nome e Cognome", label_visibility="collapsed")
            p2_final = p2_new if p2_new != "" else p2_sel

            paid = st.checkbox("Quota d'iscrizione versata (€)")
            
            submit = st.form_submit_button("CONFERMA ISCRIZIONE", use_container_width=True)
            
            if submit:
                if team_final != "-" and p1_final != "-" and p2_final != "-":
                    # Salvataggio dati
                    nuovo_team = {
                        "full": f"{team_final} ({p1_final}/{p2_final})", 
                        "name": team_final, 
                        "p1": p1_final, 
                        "p2": p2_final, 
                        "paid": paid
                    }
                    st.session_state['teams'].append(nuovo_team)
                    
                    # Aggiornamento Database Persistente (Atleti e Team)
                    if team_final not in st.session_state['db_teams']: 
                        st.session_state['db_teams'].append(team_final)
                    
                    for p in [p1_final, p2_final]:
                        if p not in st.session_state['db_atleti']: 
                            st.session_state['db_atleti'].append(p)
                        if p not in st.session_state['ranking_atleti']:
                            st.session_state['ranking_atleti'][p] = 0
                    
                    st.rerun() # Ricarica per aggiornare counter e lista
                else:
                    st.error("Errore: Compila tutti i campi prima di confermare!")

    with col2:
        st.subheader("📋 Lista Check-in")
        if not st.session_state['teams']:
            st.info("Nessuna squadra iscritta al momento.")
        else:
            for t in st.session_state['teams']:
                check = "🟢 Pagato" if t['paid'] else "🔴 Non Pagato"
                st.write(f"{check} | **{t['full']}**")
        
        st.write("---")
        st.session_state['min_teams'] = st.number_input("Soglia minima squadre per iniziare:", 4, 32, value=st.session_state['min_teams'])
        
        if len(st.session_state['teams']) >= st.session_state['min_teams']:
            if st.button("🚀 AVVIA TORNEO", use_container_width=True):
                st.session_state['phase'] = "Gironi"
                # Generazione automatica calendario Round Robin
                lt = st.session_state['teams']
                st.session_state['matches'] = []
                for i in range(len(lt)):
                    for j in range(i+1, len(lt)):
                        st.session_state['matches'].append({"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False})
                st.rerun()

elif st.session_state['phase'] == "Gironi":
    st.header("🎾 FASE A GIRONI")
    tab1, tab2 = st.tabs(["🏟️ Calendario Match", "📈 Classifica Live"])
    
    with tab1:
        match_da_fare = [m for m in st.session_state['matches'] if not m['Fatto']]
        if not match_da_fare:
            st.success("Tutti i match sono stati completati!")
        else:
            for idx, m in enumerate(st.session_state['matches']):
                if not m['Fatto']:
                    with st.expander(f"Match: {m['A']['name']} vs {m['B']['name']}"):
                        ris = st.selectbox("Punteggio Set", ["2-0", "2-1", "1-2", "0-2"], key=f"match_{idx}")
                        if st.button("Salva Risultato", key=f"save_{idx}"):
                            va, vb = map(int, ris.split("-"))
                            st.session_state['matches'][idx].update({"SA": va, "SB": vb, "Fatto": True})
                            st.rerun()

    with tab2:
        # Calcolo classifica dinamica
        classifica = {t['full']: {"Punti": 0, "Set Vinti": 0} for t in st.session_state['teams']}
        for m in st.session_state['matches']:
            if m['Fatto']:
                classifica[m['A']['full']]["Set Vinti"] += m['SA']
                classifica[m['B']['full']]["Set Vinti"] += m['SB']
                if m['SA'] > m['SB']: classifica[m['A']['full']]["Punti"] += 3
                else: classifica[m['B']['full']]["Punti"] += 3
        
        df = pd.DataFrame.from_dict(classifica, orient='index').reset_index().sort_values(by=["Punti", "Set Vinti"], ascending=False)
        st.table(df)

        if all(m['Fatto'] for m in st.session_state['matches']):
            if st.button("🏆 PROCEDI AI PLAYOFF", use_container_width=True):
                top_4_names = df["index"].tolist()[:4]
                # Recupero oggetti team completi
                top_teams = [next(t for t in st.session_state['teams'] if t['full'] == n) for n in top_4_names]
                st.session_state['playoffs'] = [
                    {"N": "Semi 1", "A": top_teams[0], "B": top_teams[3], "V": None, "L": None},
                    {"N": "Semi 2", "A": top_teams[1], "B": top_teams[2], "V": None, "L": None}
                ]
                st.session_state['phase'] = "Playoff"
                st.rerun()

elif st.session_state['phase'] == "Playoff":
    st.header("🏁 FINAL FOUR")
    
    

    col_a, col_b = st.columns(2)
    for i in range(2):
        with [col_a, col_b][i]:
            p = st.session_state['playoffs'][i]
            st.markdown(f"<div class='bracket-box'>{p['A']['name']}<br>vs<br>{p['B']['name']}</div>", unsafe_allow_html=True)
            vincitore_semi = st.selectbox(f"Vince {p['N']}", ["-", "Team A", "Team B"], key=f"semi_{i}")
            if vincitore_semi != "-":
                st.session_state['playoffs'][i]['V'] = p['A'] if vincitore_semi == "Team A" else p['B']
                st.session_state['playoffs'][i]['L'] = p['B'] if vincitore_semi == "Team A" else p['A']

    if all(p['V'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
        if st.button("✨ GENERA FINALI"):
            st.session_state['playoffs'].append({"N": "FINALE 1° POSTO", "A": st.session_state['playoffs'][0]['V'], "B": st.session_state['playoffs'][1]['V'], "V": None})
            st.session_state['playoffs'].append({"N": "FINALE 3° POSTO", "A": st.session_state['playoffs'][0]['L'], "B": st.session_state['playoffs'][1]['L'], "V": None})
            st.rerun()

    if len(st.session_state['playoffs']) > 2:
        f1 = st.session_state['playoffs'][2]
        st.markdown(f"<div class='bracket-box' style='border-color:gold;'>ORO: {f1['A']['name']} vs {f1['B']['name']}</div>", unsafe_allow_html=True)
        campione = st.selectbox("VINCITORE TORNEO:", ["-", f1['A']['name'], f1['B']['name']], key="gold_winner")
        
        if campione != "-" and st.button("🏁 CHIUDI TORNEO E ASSEGNA RANKING"):
            vincitore_finale = f1['A'] if campione == f1['A']['name'] else f1['B']
            # Punti = Numero Coppie * 10
            punti_vittoria = len(st.session_state['teams']) * 10
            
            st.session_state['ranking_atleti'][vincitore_finale['p1']] += punti_vittoria
            st.session_state['ranking_atleti'][vincitore_finale['p2']] += punti_vittoria
            st.session_state['albo_oro'].append(f"🏆 {vincitore_finale['name']} ({vincitore_finale['p1']}/{vincitore_finale['p2']})")
            
            # Reset torneo per il prossimo
            st.session_state['phase'] = "Setup"
            st.session_state['teams'] = []
            st.balloons()
            st.rerun()
