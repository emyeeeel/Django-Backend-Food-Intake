from django.urls import path, include
from rest_framework.routers import DefaultRouter
from meals.views import (
    MealAssignmentViewSet,
    MealViewSet,
    FoodIntakeListCreateView,
    FoodIntakeDetailView
)

router = DefaultRouter()
router.register(r'meals', MealViewSet)
router.register(r'meal-assignments', MealAssignmentViewSet)

urlpatterns = [
    # Meals - trailing slash
    path('meals/', MealViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='meals'),
    path('meals/<int:pk>/', MealViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='meal-detail'),

    # Meals - no trailing slash
    path('meals', MealViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='meals-no-slash'),
    path('meals/<int:pk>', MealViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='meal-detail-no-slash'),

    # MealAssignments - trailing slash
    path('meal-assignments/', MealAssignmentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='meal-assignments'),
    path('meal-assignments/<int:pk>/', MealAssignmentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='meal-assignment-detail'),

    # MealAssignments - no trailing slash
    path('meal-assignments', MealAssignmentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='meal-assignments-no-slash'),
    path('meal-assignments/<int:pk>', MealAssignmentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='meal-assignment-detail-no-slash'),

    # FoodIntake - trailing slash
    path('food-intake/', FoodIntakeListCreateView.as_view(), name='food-intake-list-create'),
    path('food-intake/<int:pk>/', FoodIntakeDetailView.as_view(), name='food-intake-detail'),

    # FoodIntake - no trailing slash
    path('food-intake', FoodIntakeListCreateView.as_view(), name='food-intake-list-create-no-slash'),
    path('food-intake/<int:pk>', FoodIntakeDetailView.as_view(), name='food-intake-detail-no-slash'),

    # Fallback router
    path('', include(router.urls)),
]
