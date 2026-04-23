import streamlit as st
from auth_guard import require_auth
from api import client

st.set_page_config(page_title='Notifications', page_icon='🔔', layout='wide')
require_auth()

st.title('🔔 Notifications')

TYPE_ICON = {
    'order_created':   '🛒',
    'product_created': '📦',
}


def load_users():
    resp = client.get('/users/')
    return resp.json() if resp.status_code == 200 else []


def load_notifications(user_id):
    resp = client.get('/notifications/', params={'user_id': user_id})
    return resp.json() if resp.status_code == 200 else []


users        = load_users()
user_options = {f"{u['full_name']} ({u['email']})": u['id'] for u in users}

selected = st.selectbox('View notifications for', ['— select user —'] + list(user_options.keys()))

if selected == '— select user —':
    st.info('Select a user to see their notifications.')
    st.stop()

user_id       = user_options[selected]
notifications = load_notifications(user_id)

if not notifications:
    st.info('No notifications for this user.')
    st.stop()

unread_count = sum(1 for n in notifications if not n['is_read'])

col1, col2 = st.columns([4, 1])
col1.markdown(f"**{len(notifications)}** notifications &nbsp; · &nbsp; **{unread_count}** unread")

with col2:
    if unread_count > 0:
        if st.button('✅ Mark all read', use_container_width=True):
            resp = client.patch('/notifications/read-all/', json={'user_id': user_id})
            if resp.status_code == 200:
                count = resp.json().get('marked_read', 0)
                st.success(f'Marked {count} as read.')
                st.rerun()
            else:
                st.error(resp.json())

st.divider()

for n in notifications:
    icon      = TYPE_ICON.get(n['notification_type'], '🔔')
    is_unread = not n['is_read']
    border    = True

    with st.container(border=border):
        col1, col2 = st.columns([5, 1])

        with col1:
            prefix = '🔵 ' if is_unread else ''
            st.markdown(f"**{prefix}{icon} {n['title']}**")
            st.write(n['message'])
            st.caption(f"{n['created_at'][:19].replace('T',' ')} · type: `{n['notification_type']}`")
            if n.get('metadata'):
                st.json(n['metadata'], expanded=False)

        with col2:
            if is_unread:
                if st.button('Mark read', key=f"read_{n['id']}"):
                    resp = client.patch(f"/notifications/{n['id']}/read/")
                    if resp.status_code == 204:
                        st.rerun()
                    else:
                        st.error(resp.json())
            else:
                st.caption('✓ Read')
