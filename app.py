import streamlit as st
import pandas as pd
from database import init_session, assegna_punti_finali, registra_incasso_torneo
from ui_components import load_styles, display_sidebar

# 1. SETUP AMBIENTE
st.set_page_config(page_title="Zero Skills Cup", layout="wide")
init_session()
load_styles()
display_sidebar()

# 2. FASE SETUP: ISCRIZIONI E CASSA
if st.session_state['phase'] == "Setup":
    st.title("🏐 CONFIGURAZIONE TORNEO")
    
    # Calcolo incasso corrente per le metriche
    incasso_attuale = sum(t.get('quota', 0) for t in st.session_state['teams'] if t.get('pagato', False))
    
    # Metriche in alto
    m1, m2, m3 = st.columns(3)
    m1.metric("Squadre Iscritte", len(st.session_state['teams']))
    m2.metric("Incasso Corrente", f"{incasso_attuale} €")
    m3.metric("Tornei Archiviati", len(st.session_state['storico_incassi']))

    # Creazione delle Tab per separare le funzioni
    tab_iscrizioni, tab_cassa = st.tabs(["📝 GESTIONE ISCRIZIONI", "💰 REGISTRO CASSA"])

    with tab_iscrizioni:
        col_isc, col_list = st.columns([1, 1.2])
        
        with col_isc:
            st.subheader("Iscrizione Squadra")
            with st.form("form_isc", clear_on_submit=True):
                usa_nome = st.toggle("Nome squadra personalizzato")
                nome_t = st.text_input("Nome Squadra") if usa_nome else ""
                
                st.write("**Atleta 1**")
                p1_sel = st.selectbox("DB 1", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
                p1_new = st.text_input("Nuovo Atleta 1", placeholder="Nome Atleta 1", label_visibility="collapsed")
                atleta1 = p1_new if p1_new != "" else p1_sel
                
                st.write("**Atleta 2**")
                p2_sel = st.selectbox("DB 2", ["-"] + st.session_state['db_atleti'], label_visibility="collapsed")
                p2_new = st.text_input("Nuovo Atleta 2", placeholder="Nome Atleta 2", label_visibility="collapsed")
                atleta2 = p2_new if p2_new != "" else p2_sel
                
                c_q, c_p = st.columns(2)
                quota = c_q.number_input("Quota (€)", min_value=0, value=10)
                pagato = c_p.checkbox("Pagato")
                
                if st.form_submit_button("CONFERMA ISCRIZIONE", use_container_width=True):
                    if atleta1 != "-" and atleta2 != "-":
                        nome_def = nome_t if (usa_nome and nome_t != "") else f"{atleta1[:3]}-{atleta2[:3]}".upper()
                        st.session_state['teams'].append({
                            "name": nome_def, "p1": atleta1, "p2": atleta2, 
                            "quota": quota, "pagato": pagato, "full": f"{nome_def} ({atleta1}/{atleta2})"
                        })
                        for a in [atleta1, atleta2]:
                            if a not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a)
                        st.rerun()

        with col_list:
            st.subheader("Lista Check-in")
            for i, t in enumerate(st.session_state['teams']):
                c1, c2 = st.columns([4, 1])
                p_status = "✅" if t.get('pagato', False) else "❌"
                c1.write(f"{p_status} **{t['full']}** ({t.get('quota', 0)}€)")
                if c2.button("🗑️", key=f"del_{i}"):
                    st.session_state['teams'].pop(i)
                    st.rerun()

            st.write("---")
            if len(st.session_state['teams']) >= 4:
                if st.button("🚀 AVVIA TORNEO", use_container_width=True):
                    lt = st.session_state['teams']
                    st.session_state['matches'] = [{"A": lt[i], "B": lt[j], "SA": 0, "SB": 0, "Fatto": False} 
                                                   for i in range(len(lt)) for j in range(i+1, len(lt))]
                    st.session_state['phase'] = "Gironi"
                    st.rerun()

    with tab_cassa:
        st.subheader("Registro Storico Incassi")
        if not st.session_state['storico_incassi']:
            st.info("Il registro sarà popolato alla chiusura del primo torneo.")
        else:
            df_cassa = pd.DataFrame(st.session_state['storico_incassi'])
            st.dataframe(df_cassa, use_container_width=True)
            totalone = df_cassa['totale'].sum()
            st.success(f"**Incasso Totale Storico: {totalone} €**")

# --- LE FASI SUCCESSIVE (Gironi e Playoff) RIMANGONO INVARIATE ---
# Assicurati solo di chiamare registra_incasso_torneo(st.session_state['teams']) 
# nel tasto finale del torneo come suggerito prima.
