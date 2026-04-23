import streamlit as st
from auth_guard import require_auth
from api import client

st.set_page_config(page_title='Products', page_icon='📦', layout='wide')
require_auth()

st.title('📦 Products')


def load_products():
    resp = client.get('/products/')
    return resp.json() if resp.status_code == 200 else []


# ── Create ────────────────────────────────────────────────────────────────────
with st.expander('➕ Create Product', expanded=False):
    with st.form('create_product'):
        name        = st.text_input('Name')
        description = st.text_area('Description')
        price       = st.number_input('Price', min_value=0.01, step=0.01, format='%.2f')
        stock       = st.number_input('Stock', min_value=0, step=1)
        if st.form_submit_button('Create', use_container_width=True):
            resp = client.post('/products/', json={
                'name': name, 'description': description,
                'price': str(price), 'stock': int(stock),
            })
            if resp.status_code == 201:
                st.success(f'Product "{name}" created.')
                st.rerun()
            else:
                st.error(resp.json())

st.divider()

# ── List ──────────────────────────────────────────────────────────────────────
products = load_products()

if not products:
    st.info('No products yet.')
    st.stop()

for p in products:
    with st.container(border=True):
        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            st.markdown(f"### {p['name']}")
            st.caption(p['description'])
            st.markdown(f"💲 **{p['price']}** &nbsp;&nbsp; 📦 Stock: `{p['stock']}`")

        with col2:
            # ── Edit ──────────────────────────────────────────────────────────
            with st.popover('✏️ Edit'):
                with st.form(f"edit_{p['id']}"):
                    new_name  = st.text_input('Name',  value=p['name'])
                    new_desc  = st.text_area('Description', value=p['description'])
                    new_price = st.number_input('Price', value=float(p['price']), min_value=0.01, step=0.01, format='%.2f')
                    new_stock = st.number_input('Stock', value=int(p['stock']), min_value=0, step=1)
                    if st.form_submit_button('Save'):
                        resp = client.put(f"/products/{p['id']}/", json={
                            'name': new_name, 'description': new_desc,
                            'price': str(new_price), 'stock': int(new_stock),
                        })
                        if resp.status_code == 204:
                            st.success('Updated.')
                            st.rerun()
                        else:
                            st.error(resp.json())

        with col3:
            if st.button('🗑️ Delete', key=f"del_{p['id']}"):
                resp = client.delete(f"/products/{p['id']}/")
                if resp.status_code == 204:
                    st.success('Deleted.')
                    st.rerun()
                else:
                    st.error(resp.json())
