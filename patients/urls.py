from rest_framework.routers import DefaultRouter
from patients.views import PatientViewSet

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patients')

urlpatterns = router.urls
