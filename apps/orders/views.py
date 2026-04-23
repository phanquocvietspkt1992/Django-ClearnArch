from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from infrastructure.authentication import JWTAuthentication, IsJWTAuthenticated
from .serializers import OrderSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer
from . import services


class OrderListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        orders = services.get_orders_by_user(user_id)
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        order = services.create_order(d['user_id'], d['items'], d.get('created_by', 'system'))
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]

    def get(self, request, pk):
        order = services.get_order_by_id(pk)
        return Response(OrderSerializer(order).data)


class OrderStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]

    def patch(self, request, pk):
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        services.update_order_status(pk, d['action'], d.get('updated_by', 'system'))
        return Response(status=status.HTTP_204_NO_CONTENT)
