import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from apps.users.views import UserListView, UserDetailView, UserDeactivateView
from apps.users.exceptions import NotFoundException, DomainException

factory = APIRequestFactory()


@pytest.mark.django_db
class TestUserListView:
    def test_get_all_returns_200(self):
        # Arrange
        mock_users = []
        with patch('apps.users.views.services.get_all_users', return_value=mock_users):
            # Act
            request = factory.get('/api/users/')
            response = UserListView.as_view()(request)
            # Assert
            assert response.status_code == 200

    def test_create_user_returns_201(self):
        # Arrange
        mock_user = MagicMock()
        mock_user.id = '123e4567-e89b-12d3-a456-426614174000'
        mock_user.email = 'test@test.com'
        mock_user.full_name = 'Test User'
        mock_user.phone_number = '0123456789'
        mock_user.is_active = True
        mock_user.created_at = None
        mock_user.updated_at = None
        with patch('apps.users.views.services.create_user', return_value=mock_user):
            # Act
            request = factory.post('/api/users/', {
                'email': 'test@test.com',
                'full_name': 'Test User',
                'phone_number': '0123456789',
                'password': 'secret123',
            }, format='json')
            response = UserListView.as_view()(request)
            # Assert
            assert response.status_code == 201


@pytest.mark.django_db
class TestUserDetailView:
    def test_get_by_id_when_found_returns_200(self):
        # Arrange
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_user = MagicMock()
        with patch('apps.users.views.services.get_user_by_id', return_value=mock_user):
            # Act
            request = factory.get(f'/api/users/{user_id}/')
            response = UserDetailView.as_view()(request, pk=user_id)
            # Assert
            assert response.status_code == 200

    def test_get_by_id_when_not_found_returns_404(self):
        # Arrange
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.users.views.services.get_user_by_id', side_effect=NotFoundException('User not found')):
            # Act
            request = factory.get(f'/api/users/{user_id}/')
            response = UserDetailView.as_view()(request, pk=user_id)
            # Assert
            assert response.status_code == 404

    def test_update_profile_returns_204(self):
        # Arrange
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.users.views.services.update_user_profile', return_value=MagicMock()):
            # Act
            request = factory.put(f'/api/users/{user_id}/', {
                'full_name': 'Updated Name',
                'phone_number': '0999999999',
            }, format='json')
            response = UserDetailView.as_view()(request, pk=user_id)
            # Assert
            assert response.status_code == 204

    def test_update_profile_when_not_found_returns_404(self):
        # Arrange
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.users.views.services.update_user_profile', side_effect=NotFoundException('User not found')):
            # Act
            request = factory.put(f'/api/users/{user_id}/', {
                'full_name': 'Updated Name',
                'phone_number': '0999999999',
            }, format='json')
            response = UserDetailView.as_view()(request, pk=user_id)
            # Assert
            assert response.status_code == 404


@pytest.mark.django_db
class TestUserDeactivateView:
    def test_deactivate_when_successful_returns_204(self):
        # Arrange
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.users.views.services.deactivate_user', return_value=None):
            # Act
            request = factory.post(f'/api/users/{user_id}/deactivate/')
            response = UserDeactivateView.as_view()(request, pk=user_id)
            # Assert
            assert response.status_code == 204

    def test_deactivate_when_already_inactive_returns_400(self):
        # Arrange
        user_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.users.views.services.deactivate_user', side_effect=DomainException('User is already inactive.')):
            # Act
            request = factory.post(f'/api/users/{user_id}/deactivate/')
            response = UserDeactivateView.as_view()(request, pk=user_id)
            # Assert
            assert response.status_code == 400
