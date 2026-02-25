import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_session, assegna_punti_finali, registra_incasso_torneo, aggiorna_database_storico, chiudi_torneo_atleta
from ui_components import load_styles, display_sidebar
import scoreboard # Il nuovo file per il tabellone moderno

# --- 1. CONFIGURAZIONE INIZIALE ---
st.set_page_config(page_title="Zero Skills Cup Pro", layout="wide")
init_session()
load_styles()
display_sidebar()

# --- 2. LOGICA DI COLLEGAMENTO SEGNAPUNTI LIVE ---
if st.session_state['phase'] in ["Gironi", "Playoff"]:
    with st.sidebar:
        st.write("---")
        st.subheader("📟 STRUMENTI ARBITRO")
        show_sb = st.toggle("Apri Segnapunti Live Pro", value=False)
    
    if show_sb:
        # Seleziona squadre reali per il segnapunti
        if st.session_state['teams']:
            col_sb1, col_sb2 = st.columns(2)
            s_a = col_sb1.selectbox("Team RED", [t['name'] for t in st.session_state['teams']], index=0)
            s_b = col_sb2.selectbox("Team BLUE", [t['name'] for t in st.session_state['teams']], index=min(1, len(st.session_state['teams'])-1))
            
            # Passa i nomi al modulo scoreboard
            scoreboard.init_scoreboard_state()
            st.session_state.sb["team_a"] = s_a
            st.session_state.sb["team_b"] = s_b
            
            # Renderizza il tabellone moderno
            scoreboard.pro_scoreboard_ui()

            # Sostituire il contenuto della funzione input_match_pro (circa rigo 35)
    st.markdown(f"""
    <div class="match-card-broadcast">
        <div class="broadcast-row row-red">🔴 <b>{m['A']['name']}</b></div>
        <div class="broadcast-row row-blue">🔵 <b>{m['B']['name']}</b></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    m['S1A'] = col1.number_input(f"S1 {m['A']['name']}", 0, 40, m.get('S1A',0), key=f"{key_prefix}1a")
    m['S1B'] = col1.number_input(f"S1 {m['B']['name']}", 0, 40, m.get('S1B',0), key=f"{key_prefix}1b")
    
    if st.session_state['match_type'] == "Best of 3":
        m['S2A'] = col2.number_input(f"S2 {m['A']['name']}", 0, 40, m.get('S2A',0), key=f"{key_prefix}2a")
        m['S2B'] = col2.number_input(f"S2 {m['B']['name']}", 0, 40, m.get('S2B',0), key=f"{key_prefix}2b")
        if (m['S1A'] > m['S1B'] and m['S2A'] < m['S2B']) or (m['S1A'] < m['S1B'] and m['S2A'] > m['S2B']):
            m['S3A'] = col3.number_input(f"S3 {m['A']['name']}", 0, 40, m.get('S3A',0), key=f"{key_prefix}3a")
            m['S3B'] = col3.number_input(f"S3 {m['B']['name']}", 0, 40, m.get('S3B',0), key=f"{key_prefix}3b")
    
    m['Fatto'] = st.checkbox("CONFERMA RISULTATO", m.get('Fatto', False), key=f"{key_prefix}f")
    return m
            # Ricezione dati dal segnapunti
            if 'ready_to_save' in st.session_state:
                st.success(f"Risultato pronto: {st.session_state.ready_to_save['set_a']} - {st.session_state.ready_to_save['set_b']}")
                st.info("Trascrivi i set nel match corrispondente qui sotto e conferma.")

# --- 3. FUNZIONE UNIVERSALE INPUT MATCH (VECCHI PROGRESSI + TIEBREAK) ---
def input_match_pro(m, key_prefix):
    with st.expander(f"🏟️ {m.get('N', 'Match')}: {m['A']['name']} vs {m['B']['name']}"):
        if m['B']['name'] == "BYE":
            st.warning("Squadra in riposo. Vittoria automatica.")
            m['S1A'], m['S1B'], m['Fatto'] = 21, 0, True
            return m

        c1, c2 = st.columns(2)
        # Set 1 (Sempre presente)
        m['S1A'] = c1.number_input(f"S1 {m['A']['name']}", 0, 30, m.get('S1A', 0), key=f"{key_prefix}1a")
        m['S1B'] = c2.number_input(f"S1 {m['B']['name']}", 0, 30, m.get('S1B', 0), key=f"{key_prefix}1b")
        
        # Logica Best of 3 (Progressi precedenti)
        if st.session_state.get('match_type') == "Best of 3":
            m['S2A'] = c1.number_input(f"S2 {m['A']['name']}", 0, 30, m.get('S2A', 0), key=f"{key_prefix}2a")
            m['S2B'] = c2.number_input(f"S2 {m['B']['name']}", 0, 30, m.get('S2B', 0), key=f"{key_prefix}2b")
            
            # Tie-break automatico se 1-1
            set_a = (1 if m['S1A'] > m['S1B'] else 0) + (1 if m['S2A'] > m['S2B'] else 0)
            set_b = (1 if m['S1B'] > m['S1A'] else 0) + (1 if m['S2B'] > m['S2A'] else 0)
            
            if set_a == 1 and set_b == 1:
                st.info("🔢 Tie-break necessario")
                m['S3A'] = c1.number_input(f"TIE {m['A']['name']}", 0, 20, m.get('S3A', 0), key=f"{key_prefix}3a")
                m['S3B'] = c2.number_input(f"TIE {m['B']['name']}", 0, 20, m.get('S3B', 0), key=f"{key_prefix}3b")
            else:
                m['S3A'], m['S3B'] = 0, 0
        
        m['Fatto'] = st.checkbox("Conferma e Salva Statistiche", m.get('Fatto', False), key=f"{key_prefix}f")
        return m

# --- 4. FASE SETUP ---
if st.session_state['phase'] == "Setup":
    # Aggiungere circa al rigo 95
        if st.session_state['settings']['formato_torneo'] == "Doppia Eliminazione":
            # Logica semplificata per inizializzare il tabellone a doppia eliminazione
            st.session_state['matches'] = [{"N": f"Winner R1 - G{i+1}", "A": teams_list[i], "B": teams_list[i+1], "Fatto": False} for i in range(0, len(teams_list)-1, 2)]
    st.title("🏐 ZERO SKILLS CUP - DASHBOARD")
    # Aggiungere circa al rigo 75
    with st.expander("⚙️ IMPOSTAZIONI TECNICHE TORNEO"):
        c1, c2, c3 = st.columns(3)
        st.session_state['settings']['formato_torneo'] = c1.selectbox("Formato", ["Gironi + Playoff", "Doppia Eliminazione"])
        st.session_state['settings']['punti_set'] = c2.number_input("Punti Set", 1, 30, 21)
        st.session_state['settings']['punti_tiebreak'] = c3.number_input("Punti Tiebreak", 1, 21, 15)
    st.markdown("<div class='mega-counter'><h1>Configurazione Torneo</h1></div>", unsafe_allow_html=True)
    
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        st.session_state['match_type'] = st.radio("Formato Partita:", ["Set Unico", "Best of 3"], help="Scegli se giocare un set secco o al meglio dei 3")
    
    with st.form("iscrizione_squadre", clear_on_submit=True):
        c1, c2 = st.columns(2)
        a1 = c1.text_input("Nome Atleta 1")
        a2 = c2.text_input("Nome Atleta 2")
        quota = st.number_input("Quota iscrizione (€)", 10)
        pagato = st.checkbox("Quota Versata")
        if st.form_submit_button("Iscrivi Squadra"):
            if a1 and a2:
                nome_squadra = f"{a1[:3]}-{a2[:3]}".upper()
                st.session_state['teams'].append({
                    "name": nome_squadra, "p1": a1, "p2": a2, 
                    "quota": quota, "pagato": pagato, 
                    "full": f"{nome_squadra} ({a1}/{a2})"
                })
                if a1 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a1)
                if a2 not in st.session_state['db_atleti']: st.session_state['db_atleti'].append(a2)
                st.rerun()

    st.subheader("Squadre Iscritte")
    for t in st.session_state['teams']:
        st.write(f"✅ {t['full']} - {'💰 Pagato' if t['pagato'] else '❌ Non Pagato'}")
    
    if len(st.session_state['teams']) >= 3 and st.button("🚀 GENERA CALENDARIO"):
        teams_list = st.session_state['teams'].copy()
        # Automazione BYE (Progressi precedenti)
        if len(teams_list) % 2 != 0:
            teams_list.append({"name": "BYE", "p1": "N/A", "p2": "N/A"})
        
        st.session_state['matches'] = [
            {"N": f"Gara {i+1}", "A": teams_list[i], "B": teams_list[j], "Fatto": False} 
            for i in range(len(teams_list)) for j in range(i+1, len(teams_list))
        ]
        st.session_state['phase'] = "Gironi"; st.rerun()

# --- 5. FASE GIRONI ---
elif st.session_state['phase'] == "Gironi":
    st.title("🎾 CLASSIFICA E GARE")
    
    for i, m in enumerate(st.session_state['matches']):
        st.session_state['matches'][i] = input_match_pro(m, f"g{i}")
    
    # Calcolo Classifica Analitica (Progressi storici integrali)
    stats = {t['full']: {"P":0, "SV":0, "SP":0, "PF":0, "PS":0, "obj":t} for t in st.session_state['teams']}
    for m in st.session_state['matches']:
        if m['Fatto'] and m['B']['name'] != "BYE":
            # Calcolo set vinti nel match
            sa = (1 if m['S1A']>m['S1B'] else 0) + (1 if m.get('S2A',0)>m.get('S2B',0) else 0) + (1 if m.get('S3A',0)>m.get('S3B',0) else 0)
            sb = (1 if m['S1B']>m['S1A'] else 0) + (1 if m.get('S2B',0)>m.get('S2A',0) else 0) + (1 if m.get('S3B',0)>m.get('S3A',0) else 0)
            
            stats[m['A']['full']]['SV'] += sa; stats[m['A']['full']]['SP'] += sb
            stats[m['B']['full']]['SV'] += sb; stats[m['B']['full']]['SP'] += sa
            stats[m['A']['full']]['PF'] += (m['S1A'] + m.get('S2A',0) + m.get('S3A',0))
            stats[m['A']['full']]['PS'] += (m['S1B'] + m.get('S2B',0) + m.get('S3B',0))
            stats[m['B']['full']]['PF'] += (m['S1B'] + m.get('S2B',0) + m.get('S3B',0))
            stats[m['B']['full']]['PS'] += (m['S1A'] + m.get('S2A',0) + m.get('S3A',0))
            if sa > sb: stats[m['A']['full']]['P'] += 3
            else: stats[m['B']['full']]['P'] += 3

    df_classifica = pd.DataFrame.from_dict(stats, orient='index').reset_index()
    df_classifica = df_classifica.sort_values(by=["P", "SV", "PF"], ascending=False)
    st.table(df_classifica[['index', 'P', 'SV', 'SP', 'PF', 'PS']])
    
    if st.button("🏆 PASSA AI PLAYOFF (TOP 4)"):
        top_4 = [stats[name]['obj'] for name in df_classifica['index'][:4]]
        st.session_state['playoffs'] = [
            {"N": "Semifinale 1", "A": top_4[0], "B": top_4[3], "Fatto": False},
            {"N": "Semifinale 2", "A": top_4[1], "B": top_4[2], "Fatto": False}
        ]
        st.session_state['phase'] = "Playoff"; st.rerun()

# --- 6. FASE PLAYOFF (BRACKET) ---
elif st.session_state['phase'] == "Playoff":
    st.title("🔥 FASE ELIMINATORIA")
    
    col_sf, col_f = st.columns(2) # Formato Bracket (Progressi precedenti)
    
    with col_sf:
        st.subheader("🛡️ Semifinali")
        for i in range(2):
            st.session_state['playoffs'][i] = input_match_pro(st.session_state['playoffs'][i], f"p{i}")
        
        if all(p['Fatto'] for p in st.session_state['playoffs'][:2]) and len(st.session_state['playoffs']) == 2:
            if st.button("Genera Finali ➔"):
                def win(m): return m['A'] if (m['S1A']+m.get('S2A',0)+m.get('S3A',0)) > (m['S1B']+m.get('S2B',0)+m.get('S3B',0)) else m['B']
                def los(m): return m['B'] if (m['S1A']+m.get('S2A',0)+m.get('S3A',0)) > (m['S1B']+m.get('S2B',0)+m.get('S3B',0)) else m['A']
                st.session_state['playoffs'].append({"N": "🥇 FINALE 1°", "A": win(st.session_state['playoffs'][0]), "B": win(st.session_state['playoffs'][1]), "Fatto": False})
                st.session_state['playoffs'].append({"N": "🥉 FINALE 3°", "A": los(st.session_state['playoffs'][0]), "B": los(st.session_state['playoffs'][1]), "Fatto": False})
                st.rerun()

    with col_f:
        if len(st.session_state['playoffs']) > 2:
            st.subheader("🏆 Finali")
            for i in range(2, 4):
                st.session_state['playoffs'][i] = input_match_pro(st.session_state['playoffs'][i], f"f{i}")
            
            if all(f['Fatto'] for f in st.session_state['playoffs'][2:]):
                if st.button("🏁 ARCHIVIA E PROCLAMA"):
                    # 1. Cassa e Ranking
                    registra_incasso_torneo(st.session_state['teams'])
                    assegna_punti_finali(st.session_state['teams'])
                    
                    # 2. Aggiornamento Profili Atleti (Tutti i match)
                    tutti_i_match = st.session_state['matches'] + st.session_state['playoffs']
                    for m in tutti_i_match:
                        if m['Fatto'] and m['B']['name'] != "BYE":
                            for atleta, pf, ps, sv, sp in [
                                (m['A']['p1'], (m['S1A']+m.get('S2A',0)+m.get('S3A',0)), (m['S1B']+m.get('S2B',0)+m.get('S3B',0)), (1 if m['S1A']>m['S1B'] else 0), (1 if m['S1B']>m['S1A'] else 0)),
                                (m['B']['p1'], (m['S1B']+m.get('S2B',0)+m.get('S3B',0)), (m['S1A']+m.get('S2A',0)+m.get('S3A',0)), (1 if m['S1B']>m['S1A'] else 0), (1 if m['S1A']>m['S1B'] else 0))
                            ]:
                                aggiorna_database_storico(atleta, pf, ps, sv, sp, 1 if sv > sp else 0, 0)
                    
                    # 3. Vincitore e Albo d'Oro
                    finale = st.session_state['playoffs'][2]
                    vincitore = finale['A'] if (finale['S1A']+finale.get('S2A',0)+finale.get('S3A',0)) > (finale['S1B']+finale.get('S2B',0)+finale.get('S3B',0)) else finale['B']
                    st.session_state['campione_nome'] = vincitore['name']
                    st.session_state['albo_oro'].append(f"🏆 {vincitore['name']} ({datetime.now().strftime('%d/%m/%Y')})")
                    st.session_state['phase'] = "Vittoria"; st.rerun()

# --- 7. SCHERMATA VITTORIA (ANIMAZIONI) ---
elif st.session_state['phase'] == "Vittoria":
    st.markdown(f"""
        <div class='winner-card'>
            <h1>🥇 VINCITORI TORNEO 🥇</h1>
            <h1 style='font-size: 100px;'>{st.session_state.get('campione_nome', 'CAMPIONI')}</h1>
            <p>I dati sono stati salvati permanentemente nei profili atleti.</p>
        </div>
    """, unsafe_allow_html=True)
    st.balloons()
    if st.button("TORNA AL MENU PRINCIPALE"):
        st.session_state['teams'] = []; st.session_state['phase'] = "Setup"; st.rerun()

import ranking_page # Importa il nuovo file

# Sotto la gestione della sidebar (display_sidebar())
with st.sidebar:
    st.write("---")
    menu = st.radio("SPOSTATI IN:", ["Torneo Live", "Hall of Fame 🏆"])

if menu == "Hall of Fame 🏆":
    ranking_page.show_podium()
    st.stop() # Interrompe l'app qui per mostrare solo la classifica

import simulator # Da aggiungere in alto insieme agli altri import

# All'interno di elif st.session_state['phase'] == "Gironi":
# O all'interno di elif st.session_state['phase'] == "Playoff":

with st.sidebar:
    st.write("---")
    st.subheader("🛠️ TOOLS SVILUPPATORE")
    if st.button("🎲 SIMULA RISULTATI MANCANTI", use_container_width=True):
        simulator.simulate_random_tournament()
        st.rerun()
