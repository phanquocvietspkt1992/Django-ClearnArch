import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from rest_framework.test import APIRequestFactory
from apps.notifications.views import NotificationListView, NotificationReadView, NotificationReadAllView
from apps.notifications.models import Notification, NotificationType
from apps.users.exceptions import NotFoundException

factory = APIRequestFactory()

USER_ID = '223e4567-e89b-12d3-a456-426614174001'
NOTIF_ID = '523e4567-e89b-12d3-a456-426614174004'


def _mock_notification():
    n = MagicMock(spec=Notification)
    n.id = NOTIF_ID
    n.user_id = USER_ID
    n.notification_type = NotificationType.ORDER_CREATED
    n.title = 'Order Placed'
    n.message = 'Your order has been placed successfully. Total: 99.99'
    n.metadata = {'order_id': 'abc123'}
    n.is_read = False
    n.created_at = datetime.now(timezone.utc)
    return n


@pytest.mark.django_db
class TestNotificationListView:
    def test_get_by_user_returns_200(self):
        with patch('apps.notifications.views.services.get_notifications_by_user', return_value=[_mock_notification()]):
            request = factory.get('/api/notifications/', {'user_id': USER_ID})
            response = NotificationListView.as_view()(request)
            assert response.status_code == 200
            assert len(response.data) == 1

    def test_missing_user_id_returns_400(self):
        request = factory.get('/api/notifications/')
        response = NotificationListView.as_view()(request)
        assert response.status_code == 400

    def test_returns_empty_list(self):
        with patch('apps.notifications.views.services.get_notifications_by_user', return_value=[]):
            request = factory.get('/api/notifications/', {'user_id': USER_ID})
            response = NotificationListView.as_view()(request)
            assert response.status_code == 200
            assert response.data == []


@pytest.mark.django_db
class TestNotificationReadView:
    def test_mark_as_read_returns_204(self):
        with patch('apps.notifications.views.services.mark_as_read', return_value=None):
            request = factory.patch(f'/api/notifications/{NOTIF_ID}/read/')
            response = NotificationReadView.as_view()(request, pk=NOTIF_ID)
            assert response.status_code == 204

    def test_mark_as_read_not_found_returns_404(self):
        with patch('apps.notifications.views.services.mark_as_read', side_effect=NotFoundException('Not found')):
            request = factory.patch(f'/api/notifications/{NOTIF_ID}/read/')
            response = NotificationReadView.as_view()(request, pk=NOTIF_ID)
            assert response.status_code == 404


@pytest.mark.django_db
class TestNotificationReadAllView:
    def test_mark_all_as_read_returns_200_with_count(self):
        with patch('apps.notifications.views.services.mark_all_as_read', return_value=3):
            request = factory.patch('/api/notifications/read-all/', {'user_id': USER_ID}, format='json')
            response = NotificationReadAllView.as_view()(request)
            assert response.status_code == 200
            assert response.data['marked_read'] == 3

    def test_missing_user_id_returns_400(self):
        request = factory.patch('/api/notifications/read-all/', {}, format='json')
        response = NotificationReadAllView.as_view()(request)
        assert response.status_code == 400


@pytest.mark.django_db
class TestNotificationModel:
    def test_for_order_created_sets_correct_fields(self):
        n = Notification.for_order_created(USER_ID, 'order-001', '199.99')
        assert n.notification_type == NotificationType.ORDER_CREATED
        assert n.user_id == USER_ID
        assert 'order-001' in n.metadata['order_id']
        assert '199.99' in n.message

    def test_for_product_created_sets_system_user(self):
        n = Notification.for_product_created('prod-001', 'Laptop', '999.00')
        assert n.notification_type == NotificationType.PRODUCT_CREATED
        assert n.user_id == 'system'
        assert 'Laptop' in n.message

    def test_to_doc_and_from_doc_roundtrip(self):
        n = Notification.for_order_created(USER_ID, 'order-001', '199.99')
        doc = n.to_doc()
        restored = Notification.from_doc(doc)
        assert restored.id == n.id
        assert restored.user_id == n.user_id
        assert restored.notification_type == n.notification_type
        assert restored.is_read is False
