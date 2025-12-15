from rest_framework import serializers

from backend import settings
from .models import FoodIntake, Meal, MealAssignment

class MealAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealAssignment
        fields = '__all__'

class MealSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Meal
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.image:
            data['image'] = (
                f"{settings.PUBLIC_DOMAIN}"
                f"{settings.MEDIA_URL}"
                f"{instance.image.name}"
            )
        return data

class FoodIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodIntake
        fields = ['id', 'patient', 'meal', 'weight_g', 'volume_ml', 'consumed_at']
        read_only_fields = ['id', 'consumed_at']