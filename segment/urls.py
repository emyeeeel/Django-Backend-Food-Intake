from django.urls import path
from .views import segment_view, capture_view

urlpatterns = [
    path('segment/', segment_view, name='segment'),
    path('capture/', capture_view, name='capture'),
]
