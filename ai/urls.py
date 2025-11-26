from django.urls import path
from .views import RecommendedIntakeDetail

urlpatterns = [
    path('patients/<int:patient_id>/recommended-intake/', RecommendedIntakeDetail.as_view(), name='recommended-intake'),
]
