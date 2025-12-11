from django.urls import path, include
from rest_framework.routers import DefaultRouter
from patients.views import PatientViewSet

# Initialize the router
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patients')

# Define urlpatterns explicitly to support both with and without trailing slashes
urlpatterns = [
    # With trailing slash
    path('patients/', PatientViewSet.as_view({'get': 'list'}), name='patients'),
    path('patients/<int:pk>/', PatientViewSet.as_view({'get': 'retrieve'}), name='patient-detail'),
    
    # Without trailing slash
    path('patients', PatientViewSet.as_view({'get': 'list'}), name='patients-without-slash'),
    path('patients/<int:pk>', PatientViewSet.as_view({'get': 'retrieve'}), name='patient-detail-without-slash'),

    # Include the router-generated URLs (with trailing slash)
    path('', include(router.urls)),
]
