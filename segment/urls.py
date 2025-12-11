from django.urls import path
from .views import segment_view, get_segmented_results

urlpatterns = [
    # With trailing slashes
    path('segment/<str:meal_type>/', segment_view, name='segment'),
    path("segment/results/", get_segmented_results, name="segment_results"),

    # Without trailing slashes
    path('segment/<str:meal_type>', segment_view, name='segment'),
    path("segment/results", get_segmented_results, name="segment_results"),
]
