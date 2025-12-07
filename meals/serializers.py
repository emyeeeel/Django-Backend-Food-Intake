from rest_framework import serializers

from backend import settings
from .models import Meal, MealAssignment

class MealAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealAssignment
        fields = '__all__'

class MealSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            # Join PUBLIC_DOMAIN with MEDIA_URL + image path
            return f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}{obj.image.name}"
        return None
