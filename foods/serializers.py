from rest_framework import serializers
from .models import FoodGroup, Nutrient, Ingredient

class FoodGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodGroup
        fields = ['id', 'name', 'description']

class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = ['id', 'name']

class IngredientSerializer(serializers.ModelSerializer):
    food_group = serializers.PrimaryKeyRelatedField(queryset=FoodGroup.objects.all())
    nutrients = serializers.PrimaryKeyRelatedField(
        many=True,  # important for multiple nutrients
        queryset=Nutrient.objects.all()
    )

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'food_group', 'nutrients', 'image']

