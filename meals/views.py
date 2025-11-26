from rest_framework.viewsets import ModelViewSet
from .models import Meal, MealAssignment
from .serializers import MealAssignmentSerializer, MealSerializer
from django_filters.rest_framework import DjangoFilterBackend

class MealViewSet(ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

class MealAssignmentViewSet(ModelViewSet):
    queryset = MealAssignment.objects.all()
    serializer_class = MealAssignmentSerializer

    # Add filtering backend
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient', 'meal_type', 'day_cycle', 'assigned_at', 'meal']