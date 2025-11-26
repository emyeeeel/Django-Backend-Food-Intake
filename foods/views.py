from rest_framework import viewsets
from .models import FoodGroup, Nutrient, Ingredient
from .serializers import FoodGroupSerializer, NutrientSerializer, IngredientSerializer

class FoodGroupViewSet(viewsets.ModelViewSet):
    queryset = FoodGroup.objects.all()
    serializer_class = FoodGroupSerializer

class NutrientViewSet(viewsets.ModelViewSet):
    queryset = Nutrient.objects.all()
    serializer_class = NutrientSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
