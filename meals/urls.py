from django.urls import path, include
from rest_framework.routers import DefaultRouter
from meals.views import MealAssignmentViewSet, MealViewSet

router = DefaultRouter()
router.register(r'meals', MealViewSet)
router.register(r'meal-assignments', MealAssignmentViewSet)

urlpatterns = [
    # With trailing slash
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

    # Without trailing slash
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

    # Include router as fallback
    path('', include(router.urls)),
]
