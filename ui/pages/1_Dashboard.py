import streamlit as st
from auth_guard import require_auth
from api import client

st.set_page_config(page_title='Dashboard', page_icon='📊', layout='wide')
require_auth()

st.title('📊 Dashboard')

products_resp = client.get('/products/')
users_resp    = client.get('/users/')

products = products_resp.json() if products_resp.status_code == 200 else []
users    = users_resp.json()    if users_resp.status_code == 200 else []

active_users   = sum(1 for u in users if u.get('is_active'))
inactive_users = len(users) - active_users
total_stock    = sum(p.get('stock', 0) for p in products)

col1, col2, col3, col4 = st.columns(4)
col1.metric('Products',      len(products))
col2.metric('Total Stock',   total_stock)
col3.metric('Users (active)', active_users)
col4.metric('Users (inactive)', inactive_users)

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader('Recent Products')
    if products:
        for p in products[:5]:
            st.markdown(f"**{p['name']}** — ${p['price']} &nbsp; `stock: {p['stock']}`")
    else:
        st.caption('No products yet.')

with col_right:
    st.subheader('Recent Users')
    if users:
        for u in users[:5]:
            status = '🟢' if u.get('is_active') else '🔴'
            st.markdown(f"{status} **{u['full_name']}** — {u['email']}")
    else:
        st.caption('No users yet.')
