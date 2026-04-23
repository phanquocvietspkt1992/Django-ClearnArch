import streamlit as st
from auth_guard import require_auth
from api import client

st.set_page_config(page_title='Users', page_icon='👥', layout='wide')
require_auth()

st.title('👥 Users')


def load_users():
    resp = client.get('/users/')
    return resp.json() if resp.status_code == 200 else []


# ── Register new user ─────────────────────────────────────────────────────────
with st.expander('➕ Register User', expanded=False):
    with st.form('create_user'):
        email        = st.text_input('Email')
        full_name    = st.text_input('Full Name')
        phone_number = st.text_input('Phone Number')
        password     = st.text_input('Password', type='password')
        if st.form_submit_button('Register', use_container_width=True):
            resp = client.post('/users/', json={
                'email': email, 'full_name': full_name,
                'phone_number': phone_number, 'password': password,
            })
            if resp.status_code == 201:
                st.success(f'User "{full_name}" registered.')
                st.rerun()
            else:
                st.error(resp.json())

st.divider()

# ── List ──────────────────────────────────────────────────────────────────────
users = load_users()

if not users:
    st.info('No users yet.')
    st.stop()

for u in users:
    status_icon = '🟢' if u['is_active'] else '🔴'
    status_text = 'Active' if u['is_active'] else 'Inactive'

    with st.container(border=True):
        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            st.markdown(f"### {status_icon} {u['full_name']}")
            st.caption(f"{u['email']} · {u['phone_number']}")
            st.markdown(f"Status: `{status_text}` &nbsp;&nbsp; ID: `{u['id']}`")

        with col2:
            # ── Edit profile ──────────────────────────────────────────────────
            with st.popover('✏️ Edit'):
                with st.form(f"edit_{u['id']}"):
                    new_name  = st.text_input('Full Name',    value=u['full_name'])
                    new_phone = st.text_input('Phone Number', value=u['phone_number'])
                    if st.form_submit_button('Save'):
                        resp = client.put(f"/users/{u['id']}/", json={
                            'full_name': new_name, 'phone_number': new_phone,
                        })
                        if resp.status_code == 204:
                            st.success('Updated.')
                            st.rerun()
                        else:
                            st.error(resp.json())

        with col3:
            if u['is_active']:
                if st.button('🚫 Deactivate', key=f"deact_{u['id']}"):
                    resp = client.post(f"/users/{u['id']}/deactivate/")
                    if resp.status_code == 204:
                        st.success('User deactivated.')
                        st.rerun()
                    else:
                        st.error(resp.json())
            else:
                st.caption('Inactive')
