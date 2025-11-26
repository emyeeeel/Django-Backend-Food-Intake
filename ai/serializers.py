from rest_framework import serializers
from .models import RecommendedIntake

class RecommendedIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedIntake
        fields = [
            'daily_caloric_needs',
            'carbohydrate',
            'total_fiber',
            'protein',
            'fat',
            'saturated_fatty_acids',
            'trans_fatty_acids',
            'alpha_linolenic_acid',
            'linoleic_acid',
            'dietary_cholesterol',
            'total_water',
        ]
