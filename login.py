from time import sleep
import streamlit as st

from helpers.api import get_token

username = st.text_input("Informe seu Login")
password = st.text_input("Informe sua senha", type="password")
company = st.text_input("Informe o ID da empresa")

if username and password and company:
    try:
        session_token = get_token(username, password, company)
    except:
        st.error("Usuário/Senha ou o ID da empresa estão incorretos", icon="🚨")
    else:
        st.success("Logado com sucesso", icon="✅")
        sleep(1)
        st.session_state.company = company
        st.session_state.session_token=session_token
        st.switch_page("pages/main.py")
