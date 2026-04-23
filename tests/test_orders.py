import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from apps.orders.views import OrderListView, OrderDetailView, OrderStatusView
from apps.users.exceptions import NotFoundException, DomainException
from infrastructure.authentication import AuthenticatedUser

factory = APIRequestFactory()

# Bypass JWT for all order tests — auth is covered by test_auth.py
_AUTHED_USER = AuthenticatedUser('223e4567-e89b-12d3-a456-426614174001')
_AUTH_TARGET = 'infrastructure.authentication.JWTAuthentication.authenticate'
_AUTH_RETURN = (_AUTHED_USER, 'token')

ORDER_ID = '123e4567-e89b-12d3-a456-426614174000'
USER_ID = '223e4567-e89b-12d3-a456-426614174001'
PRODUCT_ID = '323e4567-e89b-12d3-a456-426614174002'


def _mock_order():
    item = MagicMock()
    item.id = '423e4567-e89b-12d3-a456-426614174003'
    item.product.id = PRODUCT_ID
    item.product.name = 'Laptop'
    item.quantity = 1
    item.unit_price = '1299.99'

    order = MagicMock()
    order.id = ORDER_ID
    order.user.id = USER_ID
    order.status = 'pending'
    order.total_price = '1299.99'
    order.items.all.return_value = [item]
    order.created_at = None
    order.updated_at = None
    return order


@pytest.mark.django_db
class TestOrderListView:
    def setup_method(self):
        self._p = patch(_AUTH_TARGET, return_value=_AUTH_RETURN)
        self._p.start()

    def teardown_method(self):
        self._p.stop()

    def test_get_orders_by_user_returns_200(self):
        with patch('apps.orders.views.services.get_orders_by_user', return_value=[]):
            request = factory.get('/api/orders/', {'user_id': USER_ID})
            response = OrderListView.as_view()(request)
            assert response.status_code == 200

    def test_get_orders_missing_user_id_returns_400(self):
        request = factory.get('/api/orders/')
        response = OrderListView.as_view()(request)
        assert response.status_code == 400

    def test_get_orders_user_not_found_returns_404(self):
        with patch('apps.orders.views.services.get_orders_by_user', side_effect=NotFoundException('Not found')):
            request = factory.get('/api/orders/', {'user_id': USER_ID})
            response = OrderListView.as_view()(request)
            assert response.status_code == 404

    def test_create_order_returns_201(self):
        mock_order = _mock_order()
        with patch('apps.orders.views.services.create_order', return_value=mock_order):
            request = factory.post('/api/orders/', {
                'user_id': USER_ID,
                'items': [{'product_id': PRODUCT_ID, 'quantity': 1}],
            }, format='json')
            response = OrderListView.as_view()(request)
            assert response.status_code == 201

    def test_create_order_user_not_found_returns_404(self):
        with patch('apps.orders.views.services.create_order', side_effect=NotFoundException('Not found')):
            request = factory.post('/api/orders/', {
                'user_id': USER_ID,
                'items': [{'product_id': PRODUCT_ID, 'quantity': 1}],
            }, format='json')
            response = OrderListView.as_view()(request)
            assert response.status_code == 404

    def test_create_order_insufficient_stock_returns_400(self):
        with patch('apps.orders.views.services.create_order', side_effect=DomainException('Insufficient stock')):
            request = factory.post('/api/orders/', {
                'user_id': USER_ID,
                'items': [{'product_id': PRODUCT_ID, 'quantity': 9999}],
            }, format='json')
            response = OrderListView.as_view()(request)
            assert response.status_code == 400


@pytest.mark.django_db
class TestOrderDetailView:
    def setup_method(self):
        self._p = patch(_AUTH_TARGET, return_value=_AUTH_RETURN)
        self._p.start()

    def teardown_method(self):
        self._p.stop()

    def test_get_by_id_when_found_returns_200(self):
        mock_order = _mock_order()
        with patch('apps.orders.views.services.get_order_by_id', return_value=mock_order):
            request = factory.get(f'/api/orders/{ORDER_ID}/')
            response = OrderDetailView.as_view()(request, pk=ORDER_ID)
            assert response.status_code == 200

    def test_get_by_id_when_not_found_returns_404(self):
        with patch('apps.orders.views.services.get_order_by_id', side_effect=NotFoundException('Not found')):
            request = factory.get(f'/api/orders/{ORDER_ID}/')
            response = OrderDetailView.as_view()(request, pk=ORDER_ID)
            assert response.status_code == 404


@pytest.mark.django_db
class TestOrderStatusView:
    def setup_method(self):
        self._p = patch(_AUTH_TARGET, return_value=_AUTH_RETURN)
        self._p.start()

    def teardown_method(self):
        self._p.stop()

    def test_confirm_order_returns_204(self):
        with patch('apps.orders.views.services.update_order_status', return_value=MagicMock()):
            request = factory.patch(f'/api/orders/{ORDER_ID}/status/', {'action': 'confirm'}, format='json')
            response = OrderStatusView.as_view()(request, pk=ORDER_ID)
            assert response.status_code == 204

    def test_cancel_order_returns_204(self):
        with patch('apps.orders.views.services.update_order_status', return_value=MagicMock()):
            request = factory.patch(f'/api/orders/{ORDER_ID}/status/', {'action': 'cancel'}, format='json')
            response = OrderStatusView.as_view()(request, pk=ORDER_ID)
            assert response.status_code == 204

    def test_invalid_action_returns_400(self):
        request = factory.patch(f'/api/orders/{ORDER_ID}/status/', {'action': 'explode'}, format='json')
        response = OrderStatusView.as_view()(request, pk=ORDER_ID)
        assert response.status_code == 400

    def test_order_not_found_returns_404(self):
        with patch('apps.orders.views.services.update_order_status', side_effect=NotFoundException('Not found')):
            request = factory.patch(f'/api/orders/{ORDER_ID}/status/', {'action': 'confirm'}, format='json')
            response = OrderStatusView.as_view()(request, pk=ORDER_ID)
            assert response.status_code == 404

    def test_invalid_transition_returns_400(self):
        with patch('apps.orders.views.services.update_order_status', side_effect=DomainException("Cannot confirm")):
            request = factory.patch(f'/api/orders/{ORDER_ID}/status/', {'action': 'confirm'}, format='json')
            response = OrderStatusView.as_view()(request, pk=ORDER_ID)
            assert response.status_code == 400
