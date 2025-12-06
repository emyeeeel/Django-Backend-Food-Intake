from rest_framework.viewsets import ModelViewSet
from .models import Meal, MealAssignment
from .serializers import MealAssignmentSerializer, MealSerializer
from django_filters.rest_framework import DjangoFilterBackend

class MealViewSet(ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

    # Ensure the request context is passed for image URLs
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class MealAssignmentViewSet(ModelViewSet):
    queryset = MealAssignment.objects.all()
    serializer_class = MealAssignmentSerializer

    # Add filtering backend
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient', 'meal_type', 'day_cycle', 'assigned_at', 'meal']

    # Pass request context if you later override serializer fields
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
