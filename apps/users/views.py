from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer
from . import services


class UserListView(APIView):
    def get(self, request):
        users = services.get_all_users()
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        user = services.create_user(d['email'], d['full_name'], d['phone_number'], d['password'], d.get('created_by', 'system'))
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    def get(self, request, pk):
        user = services.get_user_by_id(pk)
        return Response(UserSerializer(user).data)

    def put(self, request, pk):
        serializer = UpdateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        services.update_user_profile(pk, d['full_name'], d['phone_number'], d.get('updated_by', 'system'))
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDeactivateView(APIView):
    def post(self, request, pk):
        services.deactivate_user(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
