from time import sleep
import streamlit as st

from helpers.api import get_token

st.set_page_config(
    "Visão Geral", layout="wide", initial_sidebar_state="collapsed"
)

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

username = st.text_input("Informe seu Login")
password = st.text_input("Informe sua senha", type="password")
company = st.text_input("Informe o ID da empresa")

if username and password and company:
    try:
        session_token, pseudonym = get_token(username, password, company)
    except:
        st.error("Usuário/Senha ou o ID da empresa estão incorretos", icon="🚨")
    else:
        st.success("Logado com sucesso", icon="✅")
        sleep(0.5)
        st.session_state.company = company
        st.session_state.session_token = session_token
        st.session_state.pseudonym = pseudonym
        st.switch_page("pages/resumo.py")
