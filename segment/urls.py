from django.urls import path
from .views import segment_view, get_segmented_results

urlpatterns = [
    path('segment/<str:meal_type>', segment_view, name='segment'),
    path("segment/results/", get_segmented_results, name="segment_results"),
]
