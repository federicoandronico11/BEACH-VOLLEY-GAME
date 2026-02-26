import streamlit as st
import database, ui_components, simulator, random

# Inizializzazione
st.set_page_config(page_title="Zero Skills Pro App", layout="wide")
database.init_session()
ui_components.apply_pro_theme()

# Sidebar per navigazione e statistiche rapide
with st.sidebar:
    st.title("🏐 Z-SKILLS PRO")
    nav = st.radio("Menu", ["Torneo Live", "Ranking Generale"])
    st.divider()
    st.write(f"Stato: **{st.session_state.phase}**")
    if st.button("⚠️ RESET TORNEO (Nuovo)"):
        st.session_state.phase = "Setup"; st.session_state.teams = []; st.session_state.matches = []; st.session_state.playoffs = []; st.rerun()

if nav == "Ranking Generale":
    # Richiama la tua pagina ranking qui
    st.header("🏆 Hall of Fame")
    rank = sorted(st.session_state.ranking_atleti.items(), key=lambda x: x[1], reverse=True)
    for i, (n, p) in enumerate(rank):
        st.write(f"{i+1}. **{n}** - {p} PT")
    st.stop()

# --- LOGICA TORNEO LIVE ---

# FASE 1: SETUP E ISCRIZIONI
if st.session_state.phase == "Setup":
    st.header("⚙️ Configurazione Torneo")
    
    c1, c2 = st.columns(2)
    st.session_state.settings['match_type'] = c1.selectbox("Formato", ["Set Unico", "Best of 3"])
    st.session_state.settings['punti_set'] = c2.number_input("Punti Vittoria Set", 5, 30, 21)

    st.divider()
    st.subheader("👥 Iscrizione Squadre")
    
    with st.form("iscrizione", clear_on_submit=True):
        col1, col2, col3 = st.columns([2,2,1])
        # Input ibrido: Scrivi o Scegli
        a1 = col1.selectbox("Atleta 1", [""] + st.session_state.db_atleti, help="Scegli o scrivi sotto")
        a1_n = col1.text_input("Nuovo Atleta 1 (se non in lista)")
        a2 = col2.selectbox("Atleta 2", [""] + st.session_state.db_atleti)
        a2_n = col2.text_input("Nuovo Atleta 2 (se non in lista)")
        
        if st.form_submit_button("AGGIUNGI SQUADRA"):
            p1 = a1_n if a1_n else a1
            p2 = a2_n if a2_n else a2
            if p1 and p2:
                t_name = f"{p1[:3]}-{p2[:3]}".upper()
                st.session_state.teams.append({"name": t_name, "p1": p1, "p2": p2})
                # Aggiorna lista atleti globale
                for p in [p1, p2]:
                    if p not in st.session_state.db_atleti: st.session_state.db_atleti.append(p)
                st.rerun()

    st.write(f"Squadre iscritte: **{len(st.session_state.teams)}**")
    for t in st.session_state.teams: st.caption(f"✅ {t['name']} ({t['p1']} / {t['p2']})")
    
    if len(st.session_state.teams) >= 2:
        if st.button("🚀 GENERA TABELLONE GIRONI", type="primary", use_container_width=True):
            # Generazione Calendario
            teams = st.session_state.teams
            st.session_state.matches = []
            for i in range(len(teams)):
                for j in range(i+1, len(teams)):
                    st.session_state.matches.append({"A": teams[i], "B": teams[j], "S1A":0, "S1B":0, "Fatto": False})
            st.session_state.phase = "Gironi"
            st.rerun()

# FASE 2: GIRONI
elif st.session_state.phase == "Gironi":
    st.header("📺 Fase a Gironi (Broadcast)")
    
    if st.button("🎲 SIMULA TUTTI I RISULTATI GIRONI"):
        for m in st.session_state.matches:
            m['S1A'], m['S1B'] = simulator.generate_volley_score(st.session_state.settings['punti_set'])
            m['Fatto'] = True
        st.rerun()

    for i, m in enumerate(st.session_state.matches):
        with st.container():
            st.markdown(f'<div class="broadcast-card"><span class="red-t">{m["A"]["name"]}</span> vs <span class="blue-t">{m["B"]["name"]}</span></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,2])
            m['S1A'] = c1.number_input(f"Score {m['A']['name']}", 0, 45, m['S1A'], key=f"ga{i}")
            m['S1B'] = c2.number_input(f"Score {m['B']['name']}", 0, 45, m['S1B'], key=f"gb{i}")
            m['Fatto'] = c3.checkbox("Conferma Risultato", m['Fatto'], key=f"f{i}")
    
    if all(m['Fatto'] for m in st.session_state.matches):
        if st.button("🏆 PASSA ALLA FASE AD ELIMINAZIONE", type="primary", use_container_width=True):
            # Logica calcolo primi 4
            # (Semplificata: ordiniamo per vittorie)
            classifica = []
            for t in st.session_state.teams:
                win = sum(1 for m in st.session_state.matches if (m['A']['name']==t['name'] and m['S1A']>m['S1B']) or (m['B']['name']==t['name'] and m['S1B']>m['S1A']))
                classifica.append({"t": t, "w": win})
            classifica = sorted(classifica, key=lambda x: x['w'], reverse=True)
            
            # Genera Semifinali
            st.session_state.playoffs = [
                {"N": "Semifinale 1", "A": classifica[0]['t'], "B": classifica[3]['t'], "S1A":0, "S1B":0, "Fatto":False},
                {"N": "Semifinale 2", "A": classifica[1]['t'], "B": classifica[2]['t'], "S1A":0, "S1B":0, "Fatto":False}
            ]
            st.session_state.phase = "Eliminazione"
            st.rerun()

# FASE 3: ELIMINAZIONE DIRETTA
elif st.session_state.phase == "Eliminazione":
    st.header("🔥 FASE FINALE")
    
    # Visualizza Semifinali
    for i, p in enumerate(st.session_state.playoffs[:2]):
        st.subheader(p['N'])
        with st.container():
            st.markdown(f'<div class="broadcast-card">{p["A"]["name"]} VS {p["B"]["name"]}</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,1,2])
            p['S1A'] = c1.number_input("Score A", 0, 45, p['S1A'], key=f"p{i}a")
            p['S1B'] = c2.number_input("Score B", 0, 45, p['S1B'], key=f"p{i}b")
            p['Fatto'] = c3.checkbox("Conferma", p['Fatto'], key=f"pf{i}")

    # Se SF finite, genera Finale
    if all(p['Fatto'] for p in st.session_state.playoffs[:2]) and len(st.session_state.playoffs) == 2:
        if st.button("🏁 GENERA FINALISSIMA"):
            w1 = st.session_state.playoffs[0]['A'] if st.session_state.playoffs[0]['S1A'] > st.session_state.playoffs[0]['S1B'] else st.session_state.playoffs[0]['B']
            w2 = st.session_state.playoffs[1]['A'] if st.session_state.playoffs[1]['S1A'] > st.session_state.playoffs[1]['S1B'] else st.session_state.playoffs[1]['B']
            st.session_state.playoffs.append({"N": "FINALISSIMA", "A": w1, "B": w2, "S1A":0, "S1B":0, "Fatto":False})
            st.rerun()

    # Visualizza Finale
    if len(st.session_state.playoffs) > 2:
        st.divider()
        f = st.session_state.playoffs[2]
        st.error(f"🏆 {f['N']}")
        c1, c2, c3 = st.columns([1,1,2])
        f['S1A'] = c1.number_input("Score A", 0, 45, f['S1A'], key="fa")
        f['S1B'] = c2.number_input("Score B", 0, 45, f['S1B'], key="fb")
        f['Fatto'] = c3.checkbox("CONCLUDI TORNEO", f['Fatto'], key="ff")

        if f['Fatto']:
            vincitore = f['A'] if f['S1A'] > f['S1B'] else f['B']
            st.balloons()
            st.markdown(f"""
                <div style="background: linear-gradient(45deg, #ffd700, #ff8c00); padding: 50px; border-radius: 20px; text-align: center;">
                    <h1 style="color: black; font-size: 3rem;">🥇 CAMPIONI: {vincitore['name']}</h1>
                    <p style="color: black; font-size: 1.5rem;">{vincitore['p1']} & {vincitore['p2']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("💾 SALVA RISULTATI NEL RANKING"):
                # Qui la logica per mandare i dati alla hall of fame
                classifica_finale = [vincitore['name']] # (Logica per gli altri nomi)
                database.assegna_punti_ranking(classifica_finale)
                st.session_state.phase = "Setup"
                st.success("Dati salvati con successo!")
                st.rerun()
