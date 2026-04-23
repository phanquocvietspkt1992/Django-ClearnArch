from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer, CreateProductSerializer, UpdateProductSerializer
from . import services


class ProductListView(APIView):
    def get(self, request):
        products = services.get_all_products()
        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        serializer = CreateProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        product = services.create_product(d['name'], d['description'], d['price'], d['stock'], d.get('created_by', 'system'))
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    def get(self, request, pk):
        product = services.get_product_by_id(pk)
        return Response(ProductSerializer(product).data)

    def put(self, request, pk):
        serializer = UpdateProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        services.update_product(pk, d['name'], d['description'], d['price'], d['stock'], d.get('updated_by', 'system'))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk):
        services.delete_product(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
