import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from apps.reviews.views import ReviewListView, ReviewDetailView
from apps.users.exceptions import NotFoundException, DomainException

factory = APIRequestFactory()


@pytest.mark.django_db
class TestReviewListView:
    def test_get_by_product_id_returns_200(self):
        # Arrange
        with patch('apps.reviews.views.services.get_reviews_by_product', return_value=[]):
            # Act
            request = factory.get('/api/reviews/', {'product_id': '123e4567-e89b-12d3-a456-426614174000'})
            response = ReviewListView.as_view()(request)
            # Assert
            assert response.status_code == 200

    def test_get_by_user_id_returns_200(self):
        # Arrange
        with patch('apps.reviews.views.services.get_reviews_by_user', return_value=[]):
            # Act
            request = factory.get('/api/reviews/', {'user_id': '123e4567-e89b-12d3-a456-426614174000'})
            response = ReviewListView.as_view()(request)
            # Assert
            assert response.status_code == 200

    def test_get_without_params_returns_400(self):
        # Act
        request = factory.get('/api/reviews/')
        response = ReviewListView.as_view()(request)
        # Assert
        assert response.status_code == 400

    def test_get_by_product_id_when_not_found_returns_404(self):
        # Arrange
        with patch('apps.reviews.views.services.get_reviews_by_product', side_effect=NotFoundException('Not found')):
            # Act
            request = factory.get('/api/reviews/', {'product_id': '123e4567-e89b-12d3-a456-426614174000'})
            response = ReviewListView.as_view()(request)
            # Assert
            assert response.status_code == 404

    def test_get_by_user_id_when_not_found_returns_404(self):
        # Arrange
        with patch('apps.reviews.views.services.get_reviews_by_user', side_effect=NotFoundException('Not found')):
            # Act
            request = factory.get('/api/reviews/', {'user_id': '123e4567-e89b-12d3-a456-426614174000'})
            response = ReviewListView.as_view()(request)
            # Assert
            assert response.status_code == 404

    def test_create_review_returns_201(self):
        # Arrange
        mock_review = MagicMock()
        mock_review.id = '123e4567-e89b-12d3-a456-426614174000'
        mock_review.user.id = '111e4567-e89b-12d3-a456-426614174000'
        mock_review.user.full_name = 'John Doe'
        mock_review.product.id = '222e4567-e89b-12d3-a456-426614174000'
        mock_review.product.name = 'Laptop'
        mock_review.rating = 5
        mock_review.comment = 'Great product!'
        mock_review.created_at = None
        with patch('apps.reviews.views.services.create_review', return_value=mock_review):
            # Act
            request = factory.post('/api/reviews/', {
                'user_id': '111e4567-e89b-12d3-a456-426614174000',
                'product_id': '222e4567-e89b-12d3-a456-426614174000',
                'rating': 5,
                'comment': 'Great product!',
            }, format='json')
            response = ReviewListView.as_view()(request)
            # Assert
            assert response.status_code == 201

    def test_create_review_when_no_delivered_order_returns_400(self):
        # Arrange
        with patch('apps.reviews.views.services.create_review',
                   side_effect=DomainException('You can only review a product from a delivered order.')):
            # Act
            request = factory.post('/api/reviews/', {
                'user_id': '111e4567-e89b-12d3-a456-426614174000',
                'product_id': '222e4567-e89b-12d3-a456-426614174000',
                'rating': 5,
            }, format='json')
            response = ReviewListView.as_view()(request)
            # Assert
            assert response.status_code == 400

    def test_create_review_when_already_reviewed_returns_400(self):
        # Arrange
        with patch('apps.reviews.views.services.create_review',
                   side_effect=DomainException('You have already reviewed this product.')):
            # Act
            request = factory.post('/api/reviews/', {
                'user_id': '111e4567-e89b-12d3-a456-426614174000',
                'product_id': '222e4567-e89b-12d3-a456-426614174000',
                'rating': 4,
            }, format='json')
            response = ReviewListView.as_view()(request)
            # Assert
            assert response.status_code == 400

    def test_create_review_with_invalid_rating_returns_400(self):
        # Act
        request = factory.post('/api/reviews/', {
            'user_id': '111e4567-e89b-12d3-a456-426614174000',
            'product_id': '222e4567-e89b-12d3-a456-426614174000',
            'rating': 10,
        }, format='json')
        response = ReviewListView.as_view()(request)
        # Assert
        assert response.status_code == 400


@pytest.mark.django_db
class TestReviewDetailView:
    def test_delete_when_successful_returns_204(self):
        # Arrange
        review_id = '123e4567-e89b-12d3-a456-426614174000'
        user_id = '111e4567-e89b-12d3-a456-426614174000'
        with patch('apps.reviews.views.services.delete_review', return_value=None):
            # Act
            request = factory.delete(f'/api/reviews/{review_id}/?user_id={user_id}')
            response = ReviewDetailView.as_view()(request, pk=review_id)
            # Assert
            assert response.status_code == 204

    def test_delete_without_user_id_returns_400(self):
        # Arrange
        review_id = '123e4567-e89b-12d3-a456-426614174000'
        # Act
        request = factory.delete(f'/api/reviews/{review_id}/')
        response = ReviewDetailView.as_view()(request, pk=review_id)
        # Assert
        assert response.status_code == 400

    def test_delete_when_not_found_returns_404(self):
        # Arrange
        review_id = '123e4567-e89b-12d3-a456-426614174000'
        user_id = '111e4567-e89b-12d3-a456-426614174000'
        with patch('apps.reviews.views.services.delete_review', side_effect=NotFoundException('Not found')):
            # Act
            request = factory.delete(f'/api/reviews/{review_id}/?user_id={user_id}')
            response = ReviewDetailView.as_view()(request, pk=review_id)
            # Assert
            assert response.status_code == 404

    def test_delete_when_not_owner_returns_400(self):
        # Arrange
        review_id = '123e4567-e89b-12d3-a456-426614174000'
        user_id = '111e4567-e89b-12d3-a456-426614174000'
        with patch('apps.reviews.views.services.delete_review',
                   side_effect=DomainException('You can only delete your own reviews.')):
            # Act
            request = factory.delete(f'/api/reviews/{review_id}/?user_id={user_id}')
            response = ReviewDetailView.as_view()(request, pk=review_id)
            # Assert
            assert response.status_code == 400
