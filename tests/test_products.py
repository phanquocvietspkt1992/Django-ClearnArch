import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from apps.products.views import ProductListView, ProductDetailView
from apps.users.exceptions import NotFoundException

factory = APIRequestFactory()


@pytest.mark.django_db
class TestProductListView:
    def test_get_all_returns_200(self):
        # Arrange
        with patch('apps.products.views.services.get_all_products', return_value=[]):
            # Act
            request = factory.get('/api/products/')
            response = ProductListView.as_view()(request)
            # Assert
            assert response.status_code == 200

    def test_create_product_returns_201(self):
        # Arrange
        mock_product = MagicMock()
        mock_product.id = '123e4567-e89b-12d3-a456-426614174000'
        mock_product.name = 'Laptop'
        mock_product.description = 'A laptop'
        mock_product.price = '1299.99'
        mock_product.stock = 50
        mock_product.created_at = None
        mock_product.updated_at = None
        with patch('apps.products.views.services.create_product', return_value=mock_product):
            # Act
            request = factory.post('/api/products/', {
                'name': 'Laptop',
                'description': 'A laptop',
                'price': '1299.99',
                'stock': 50,
            }, format='json')
            response = ProductListView.as_view()(request)
            # Assert
            assert response.status_code == 201


@pytest.mark.django_db
class TestProductDetailView:
    def test_get_by_id_when_found_returns_200(self):
        # Arrange
        from decimal import Decimal
        product_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_product = MagicMock()
        mock_product.id = product_id
        mock_product.name = 'Laptop'
        mock_product.description = 'A laptop'
        mock_product.price = Decimal('1299.99')
        mock_product.stock = 50
        mock_product.created_at = None
        mock_product.updated_at = None
        with patch('apps.products.views.services.get_product_by_id', return_value=mock_product):
            # Act
            request = factory.get(f'/api/products/{product_id}/')
            response = ProductDetailView.as_view()(request, pk=product_id)
            # Assert
            assert response.status_code == 200

    def test_get_by_id_when_not_found_returns_404(self):
        # Arrange
        product_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.products.views.services.get_product_by_id', side_effect=NotFoundException('Not found')):
            # Act
            request = factory.get(f'/api/products/{product_id}/')
            response = ProductDetailView.as_view()(request, pk=product_id)
            # Assert
            assert response.status_code == 404

    def test_update_when_successful_returns_204(self):
        # Arrange
        product_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.products.views.services.update_product', return_value=MagicMock()):
            # Act
            request = factory.put(f'/api/products/{product_id}/', {
                'name': 'Updated Laptop',
                'description': 'Updated desc',
                'price': '999.99',
                'stock': 30,
            }, format='json')
            response = ProductDetailView.as_view()(request, pk=product_id)
            # Assert
            assert response.status_code == 204

    def test_update_when_not_found_returns_404(self):
        # Arrange
        product_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.products.views.services.update_product', side_effect=NotFoundException('Not found')):
            # Act
            request = factory.put(f'/api/products/{product_id}/', {
                'name': 'Updated Laptop',
                'description': 'Updated desc',
                'price': '999.99',
                'stock': 30,
            }, format='json')
            response = ProductDetailView.as_view()(request, pk=product_id)
            # Assert
            assert response.status_code == 404

    def test_delete_when_successful_returns_204(self):
        # Arrange
        product_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.products.views.services.delete_product', return_value=None):
            # Act
            request = factory.delete(f'/api/products/{product_id}/')
            response = ProductDetailView.as_view()(request, pk=product_id)
            # Assert
            assert response.status_code == 204

    def test_delete_when_not_found_returns_404(self):
        # Arrange
        product_id = '123e4567-e89b-12d3-a456-426614174000'
        with patch('apps.products.views.services.delete_product', side_effect=NotFoundException('Not found')):
            # Act
            request = factory.delete(f'/api/products/{product_id}/')
            response = ProductDetailView.as_view()(request, pk=product_id)
            # Assert
            assert response.status_code == 404
