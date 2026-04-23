import requests
import streamlit as st

BASE_URL = 'http://localhost:8000/api'


def _headers():
    token = st.session_state.get('access_token', '')
    return {'Authorization': f'Bearer {token}'} if token else {}


def _refresh():
    refresh_token = st.session_state.get('refresh_token', '')
    if not refresh_token:
        return False
    resp = requests.post(f'{BASE_URL}/auth/refresh/', json={'refresh_token': refresh_token})
    if resp.status_code == 200:
        data = resp.json()
        st.session_state['access_token'] = data['access_token']
        st.session_state['refresh_token'] = data['refresh_token']
        return True
    return False


def request(method, path, **kwargs):
    url = f'{BASE_URL}{path}'
    resp = requests.request(method, url, headers=_headers(), **kwargs)
    if resp.status_code == 401 and _refresh():
        resp = requests.request(method, url, headers=_headers(), **kwargs)
    return resp


def get(path, **kwargs):    return request('GET', path, **kwargs)
def post(path, **kwargs):   return request('POST', path, **kwargs)
def put(path, **kwargs):    return request('PUT', path, **kwargs)
def patch(path, **kwargs):  return request('PATCH', path, **kwargs)
def delete(path, **kwargs): return request('DELETE', path, **kwargs)
