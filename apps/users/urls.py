from django.urls import path
from .views import UserListView, UserDetailView, UserDeactivateView

urlpatterns = [
    path('users/', UserListView.as_view()),
    path('users/<uuid:pk>/', UserDetailView.as_view()),
    path('users/<uuid:pk>/deactivate/', UserDeactivateView.as_view()),
]
