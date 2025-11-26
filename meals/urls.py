from rest_framework.routers import DefaultRouter
from meals.views import MealAssignmentViewSet, MealViewSet

router = DefaultRouter()
router.register(r'meals', MealViewSet)
router.register(r'meal-assignments', MealAssignmentViewSet)

urlpatterns = router.urls
