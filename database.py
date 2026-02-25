import streamlit as st

def init_db():
    if 'db_atleti' not in st.session_state: st.session_state['db_atleti'] = []
    if 'ranking_atleti' not in st.session_state: st.session_state['ranking_atleti'] = {}
    if 'db_teams' not in st.session_state: st.session_state['db_teams'] = []
    if 'albo_oro' not in st.session_state: st.session_state['albo_oro'] = []

def save_atleta(nome):
    if nome not in st.session_state['db_atleti'] and nome != "-":
        st.session_state['db_atleti'].append(nome)
        st.session_state['ranking_atleti'][nome] = 0

def add_points(nome, punti):
    if nome in st.session_state['ranking_atleti']:
        st.session_state['ranking_atleti'][nome] += punti
