import streamlit as st


def require_auth():
    if not st.session_state.get('access_token'):
        st.warning('Please log in first.')
        st.page_link('app.py', label='Go to Login', icon='🔐')
        st.stop()
