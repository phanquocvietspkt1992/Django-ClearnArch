from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, RefreshSerializer
from . import services


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        tokens = services.login(d['email'], d['password'])
        return Response(tokens, status=status.HTTP_200_OK)


class RefreshView(APIView):
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = services.refresh(serializer.validated_data['refresh_token'])
        return Response(tokens, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.logout(serializer.validated_data['refresh_token'])
        return Response(status=status.HTTP_204_NO_CONTENT)
