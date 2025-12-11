from django.urls import path
from .views import RecommendedIntakeDetail

urlpatterns = [
    # With trailing slash
    path('patients/<int:patient_id>/recommended-intake/', RecommendedIntakeDetail.as_view(), name='recommended-intake'),

    # Without trailing slash
    path('patients/<int:patient_id>/recommended-intake', RecommendedIntakeDetail.as_view(), name='recommended-intake-without-slash'),
]
