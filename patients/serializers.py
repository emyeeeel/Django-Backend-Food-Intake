from rest_framework import serializers
from patients.models import Patient
from meals.serializers import MealAssignmentSerializer

class PatientSerializer(serializers.ModelSerializer):
    bmi = serializers.SerializerMethodField(read_only=True)
    meal_assignments = MealAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'age',
            'sex',
            'height_cm',
            'weight_kg',
            'bmi',
            'heart_rate',
            'systolic_bp',
            'diastolic_bp',
            'activity_level',
            'meal_assignments',
            'created_at',
            'updated_at',
        ]

    def get_bmi(self, obj):
        return obj.bmi