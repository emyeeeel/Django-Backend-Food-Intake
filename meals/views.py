from rest_framework.viewsets import ModelViewSet
from meals.filters import MealFilter
from .models import FoodIntake, Meal, MealAssignment
from .serializers import FoodIntakeSerializer, MealAssignmentSerializer, MealSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics


class MealViewSet(ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MealFilter

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
    
# Create / List FoodIntake
class FoodIntakeListCreateView(generics.ListCreateAPIView):
    queryset = FoodIntake.objects.all()
    serializer_class = FoodIntakeSerializer

    def get_queryset(self):
        """
        Optional filtering by patient or meal
        Example: /api/food-intake/?patient=1
        """
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        meal_id = self.request.query_params.get('meal')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if meal_id:
            queryset = queryset.filter(meal_id=meal_id)
        return queryset

# Retrieve / Update / Delete a single FoodIntake
class FoodIntakeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodIntake.objects.all()
    serializer_class = FoodIntakeSerializer
