from django.urls import path
from .views import ReviewListView, ReviewDetailView

urlpatterns = [
    path('reviews/', ReviewListView.as_view()),
    path('reviews/<uuid:pk>/', ReviewDetailView.as_view()),
]
