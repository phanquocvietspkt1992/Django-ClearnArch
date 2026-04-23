from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import NotificationSerializer
from . import services


class NotificationListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        notifications = services.get_notifications_by_user(user_id)
        return Response(NotificationSerializer(notifications, many=True).data)


class NotificationReadView(APIView):
    def patch(self, request, pk):
        services.mark_as_read(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationReadAllView(APIView):
    def patch(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        count = services.mark_all_as_read(user_id)
        return Response({'marked_read': count})
