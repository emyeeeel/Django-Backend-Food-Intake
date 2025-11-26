from rest_framework import serializers
from .models import Meal, MealAssignment
from patients.models import Patient  # if needed

class MealAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealAssignment
        fields = '__all__'

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'
