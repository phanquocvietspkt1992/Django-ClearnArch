import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from apps.auth.views import LoginView, RefreshView, LogoutView
from apps.orders.views import OrderListView
from apps.users.exceptions import DomainException

factory = APIRequestFactory()

USER_ID = '223e4567-e89b-12d3-a456-426614174001'
MOCK_TOKENS = {
    'access_token': 'access.token.here',
    'refresh_token': 'refresh-token-uuid',
}


@pytest.mark.django_db
class TestLoginView:
    def test_login_success_returns_200_with_tokens(self):
        with patch('apps.auth.views.services.login', return_value=MOCK_TOKENS):
            request = factory.post('/api/auth/login/', {'email': 'a@b.com', 'password': 'secret123'}, format='json')
            response = LoginView.as_view()(request)
            assert response.status_code == 200
            assert 'access_token' in response.data
            assert 'refresh_token' in response.data

    def test_login_invalid_credentials_returns_400(self):
        with patch('apps.auth.views.services.login', side_effect=DomainException('Invalid email or password.')):
            request = factory.post('/api/auth/login/', {'email': 'a@b.com', 'password': 'wrong'}, format='json')
            response = LoginView.as_view()(request)
            assert response.status_code == 400

    def test_login_inactive_user_returns_400(self):
        with patch('apps.auth.views.services.login', side_effect=DomainException('User account is inactive.')):
            request = factory.post('/api/auth/login/', {'email': 'a@b.com', 'password': 'secret123'}, format='json')
            response = LoginView.as_view()(request)
            assert response.status_code == 400

    def test_login_missing_fields_returns_400(self):
        request = factory.post('/api/auth/login/', {'email': 'a@b.com'}, format='json')
        response = LoginView.as_view()(request)
        assert response.status_code == 400


@pytest.mark.django_db
class TestRefreshView:
    def test_refresh_success_returns_200_with_new_tokens(self):
        with patch('apps.auth.views.services.refresh', return_value=MOCK_TOKENS):
            request = factory.post('/api/auth/refresh/', {'refresh_token': 'old-token'}, format='json')
            response = RefreshView.as_view()(request)
            assert response.status_code == 200
            assert 'access_token' in response.data

    def test_refresh_invalid_token_returns_400(self):
        with patch('apps.auth.views.services.refresh', side_effect=DomainException('Refresh token is invalid or expired.')):
            request = factory.post('/api/auth/refresh/', {'refresh_token': 'bad-token'}, format='json')
            response = RefreshView.as_view()(request)
            assert response.status_code == 400


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_returns_204(self):
        with patch('apps.auth.views.services.logout', return_value=None):
            request = factory.post('/api/auth/logout/', {'refresh_token': 'some-token'}, format='json')
            response = LogoutView.as_view()(request)
            assert response.status_code == 204


@pytest.mark.django_db
class TestJWTProtectedOrders:
    def test_orders_without_token_returns_403(self):
        request = factory.get('/api/orders/', {'user_id': USER_ID})
        response = OrderListView.as_view()(request)
        assert response.status_code == 403

    def test_orders_with_invalid_token_returns_403(self):
        request = factory.get('/api/orders/', {'user_id': USER_ID}, HTTP_AUTHORIZATION='Bearer bad.token.here')
        response = OrderListView.as_view()(request)
        assert response.status_code == 403

    def test_orders_with_valid_token_returns_200(self):
        from infrastructure.authentication import AuthenticatedUser
        with patch('infrastructure.authentication.jwt_utils.decode_access_token', return_value=USER_ID):
            with patch('apps.orders.views.services.get_orders_by_user', return_value=[]):
                request = factory.get('/api/orders/', {'user_id': USER_ID}, HTTP_AUTHORIZATION='Bearer valid.token')
                response = OrderListView.as_view()(request)
                assert response.status_code == 200
