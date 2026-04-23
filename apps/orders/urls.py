from django.urls import path
from .views import OrderListView, OrderDetailView, OrderStatusView

urlpatterns = [
    path('orders/', OrderListView.as_view()),
    path('orders/<uuid:pk>/', OrderDetailView.as_view()),
    path('orders/<uuid:pk>/status/', OrderStatusView.as_view()),
]
