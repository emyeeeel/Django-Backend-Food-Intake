from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodGroupViewSet, NutrientViewSet, IngredientViewSet

# Initialize the router
router = DefaultRouter()
router.register(r'food-groups', FoodGroupViewSet)
router.register(r'nutrients', NutrientViewSet)
router.register(r'ingredients', IngredientViewSet)

# Define urlpatterns explicitly to support both with and without trailing slashes
urlpatterns = [
    # With trailing slashes
    path('food-groups/', FoodGroupViewSet.as_view({'get': 'list'}), name='food-groups'),
    path('food-groups/<int:pk>/', FoodGroupViewSet.as_view({'get': 'retrieve'}), name='food-group-detail'),
    
    path('nutrients/', NutrientViewSet.as_view({'get': 'list'}), name='nutrients'),
    path('nutrients/<int:pk>/', NutrientViewSet.as_view({'get': 'retrieve'}), name='nutrient-detail'),
    
    path('ingredients/', IngredientViewSet.as_view({'get': 'list'}), name='ingredients'),
    path('ingredients/<int:pk>/', IngredientViewSet.as_view({'get': 'retrieve'}), name='ingredient-detail'),

    # Without trailing slashes
    path('food-groups', FoodGroupViewSet.as_view({'get': 'list'}), name='food-groups-without-slash'),
    path('food-groups/<int:pk>', FoodGroupViewSet.as_view({'get': 'retrieve'}), name='food-group-detail-without-slash'),
    
    path('nutrients', NutrientViewSet.as_view({'get': 'list'}), name='nutrients-without-slash'),
    path('nutrients/<int:pk>', NutrientViewSet.as_view({'get': 'retrieve'}), name='nutrient-detail-without-slash'),
    
    path('ingredients', IngredientViewSet.as_view({'get': 'list'}), name='ingredients-without-slash'),
    path('ingredients/<int:pk>', IngredientViewSet.as_view({'get': 'retrieve'}), name='ingredient-detail-without-slash'),
    
    # Include the router-generated URLs (with trailing slash)
    path('', include(router.urls)),
]
