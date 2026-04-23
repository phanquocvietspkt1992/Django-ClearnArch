import streamlit as st
from auth_guard import require_auth
from api import client

st.set_page_config(page_title='Orders', page_icon='🛒', layout='wide')
require_auth()

st.title('🛒 Orders')

STATUS_ICON = {
    'pending':   '🟡',
    'confirmed': '🔵',
    'shipped':   '🚚',
    'delivered': '🟢',
    'cancelled': '🔴',
}

TRANSITIONS = {
    'pending':   [('confirm',  '✅ Confirm')],
    'confirmed': [('ship',     '🚚 Ship')],
    'shipped':   [('deliver',  '📬 Deliver')],
    'delivered': [],
    'cancelled': [],
}


def load_users():
    resp = client.get('/users/')
    return resp.json() if resp.status_code == 200 else []


def load_orders(user_id):
    resp = client.get('/orders/', params={'user_id': user_id})
    return resp.json() if resp.status_code == 200 else []


def load_products():
    resp = client.get('/products/')
    return resp.json() if resp.status_code == 200 else []


# ── Place order ───────────────────────────────────────────────────────────────
users    = load_users()
products = load_products()

user_options    = {f"{u['full_name']} ({u['email']})": u['id'] for u in users if u['is_active']}
product_options = {f"{p['name']} — ${p['price']} (stock: {p['stock']})": p['id'] for p in products}

with st.expander('➕ Place Order', expanded=False):
    with st.form('create_order'):
        selected_user    = st.selectbox('User',    list(user_options.keys()))
        selected_product = st.selectbox('Product', list(product_options.keys()))
        quantity         = st.number_input('Quantity', min_value=1, step=1)
        if st.form_submit_button('Place Order', use_container_width=True):
            user_id    = user_options[selected_user]
            product_id = product_options[selected_product]
            resp = client.post('/orders/', json={
                'user_id': user_id,
                'items': [{'product_id': product_id, 'quantity': int(quantity)}],
            })
            if resp.status_code == 201:
                st.success('Order placed!')
                st.rerun()
            else:
                st.error(resp.json())

st.divider()

# ── Filter by user ─────────────────────────────────────────────────────────────
selected_filter = st.selectbox('View orders for', ['— select user —'] + list(user_options.keys()))

if selected_filter == '— select user —':
    st.info('Select a user to see their orders.')
    st.stop()

user_id = user_options[selected_filter]
orders  = load_orders(user_id)

if not orders:
    st.info('No orders for this user.')
    st.stop()

for o in orders:
    status      = o['status']
    status_icon = STATUS_ICON.get(status, '⚪')
    transitions = TRANSITIONS.get(status, [])
    can_cancel  = status not in ('delivered', 'cancelled')

    with st.container(border=True):
        col1, col2 = st.columns([5, 2])

        with col1:
            st.markdown(f"### {status_icon} Order `{o['id'][:8]}…`")
            st.markdown(f"Status: `{status}` &nbsp;&nbsp; Total: **${o['total_price']}**")
            st.caption(f"Created: {o['created_at'][:19].replace('T',' ')}")

            # Items table
            items = o.get('items', [])
            if items:
                rows = ''.join(
                    f"<tr><td>{i['product_name']}</td><td>{i['quantity']}</td><td>${i['unit_price']}</td></tr>"
                    for i in items
                )
                st.markdown(
                    f"<table><thead><tr><th>Product</th><th>Qty</th><th>Unit Price</th></tr></thead>"
                    f"<tbody>{rows}</tbody></table>",
                    unsafe_allow_html=True,
                )

        with col2:
            for action, label in transitions:
                if st.button(label, key=f"{action}_{o['id']}"):
                    resp = client.patch(f"/orders/{o['id']}/status/", json={'action': action})
                    if resp.status_code == 204:
                        st.success(f'Order {action}ed.')
                        st.rerun()
                    else:
                        st.error(resp.json())

            if can_cancel:
                if st.button('❌ Cancel', key=f"cancel_{o['id']}"):
                    resp = client.patch(f"/orders/{o['id']}/status/", json={'action': 'cancel'})
                    if resp.status_code == 204:
                        st.success('Order cancelled.')
                        st.rerun()
                    else:
                        st.error(resp.json())
