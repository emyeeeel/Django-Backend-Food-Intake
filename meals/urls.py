from django.urls import path, include
from rest_framework.routers import DefaultRouter
from meals.views import MealAssignmentViewSet, MealViewSet

# Initialize the router
router = DefaultRouter()
router.register(r'meals', MealViewSet)
router.register(r'meal-assignments', MealAssignmentViewSet)

# Define urlpatterns explicitly to support both with and without trailing slashes
urlpatterns = [
    # With trailing slash
    path('meals/', MealViewSet.as_view({'get': 'list'}), name='meals'),
    path('meals/<int:pk>/', MealViewSet.as_view({'get': 'retrieve'}), name='meal-detail'),
    
    path('meal-assignments/', MealAssignmentViewSet.as_view({'get': 'list'}), name='meal-assignments'),
    path('meal-assignments/<int:pk>/', MealAssignmentViewSet.as_view({'get': 'retrieve'}), name='meal-assignment-detail'),

    # Without trailing slash
    path('meals', MealViewSet.as_view({'get': 'list'}), name='meals-without-slash'),
    path('meals/<int:pk>', MealViewSet.as_view({'get': 'retrieve'}), name='meal-detail-without-slash'),
    
    path('meal-assignments', MealAssignmentViewSet.as_view({'get': 'list'}), name='meal-assignments-without-slash'),
    path('meal-assignments/<int:pk>', MealAssignmentViewSet.as_view({'get': 'retrieve'}), name='meal-assignment-detail-without-slash'),

    # Include the router-generated URLs (with trailing slash)
    path('', include(router.urls)),
]
