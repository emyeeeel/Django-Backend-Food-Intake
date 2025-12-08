from django.urls import path
from .views import segment_view

urlpatterns = [
    path('segment/', segment_view, name='segment'),
]
