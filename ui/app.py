import streamlit as st
from api import client

st.set_page_config(page_title='CleanArch', page_icon='🏗️', layout='wide')

# Already logged in — redirect hint
if st.session_state.get('access_token'):
    st.success('You are logged in.')
    st.page_link('pages/1_Dashboard.py', label='Go to Dashboard →', icon='📊')
    if st.button('Logout'):
        refresh_token = st.session_state.get('refresh_token', '')
        if refresh_token:
            client.post('/auth/logout/', json={'refresh_token': refresh_token})
        st.session_state.clear()
        st.rerun()
    st.stop()

st.title('🏗️ CleanArch')
st.subheader('Login')

with st.form('login_form'):
    email = st.text_input('Email')
    password = st.text_input('Password', type='password')
    submitted = st.form_submit_button('Login', use_container_width=True)

if submitted:
    if not email or not password:
        st.error('Email and password are required.')
    else:
        resp = client.post('/auth/login/', json={'email': email, 'password': password})
        if resp.status_code == 200:
            data = resp.json()
            st.session_state['access_token'] = data['access_token']
            st.session_state['refresh_token'] = data['refresh_token']
            st.success('Logged in!')
            st.switch_page('pages/1_Dashboard.py')
        else:
            detail = resp.json().get('detail', 'Login failed.')
            st.error(detail)

st.divider()
st.caption('No account? Register via the API — POST /api/users/')
