from django.urls import path
from .views import get_segmented_results, yolo_segment_view

urlpatterns = [
    # path('segment/<str:meal_type>', segment_view, name='segment'),
    path("segment/results/", get_segmented_results, name="segment_results"),

    path("segment/<str:meal_type>", yolo_segment_view),
]
