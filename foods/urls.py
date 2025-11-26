from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodGroupViewSet, NutrientViewSet, IngredientViewSet

router = DefaultRouter()
router.register(r'food-groups', FoodGroupViewSet)
router.register(r'nutrients', NutrientViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
