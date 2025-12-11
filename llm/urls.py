from django.urls import path
from .views import MealToIngredientAPIView

urlpatterns = [
    # With trailing slash
    path('generate-ingredients-from-meal/', MealToIngredientAPIView.as_view(), name='generate-ingredients-from-meal'),

    # Without trailing slash
    path('generate-ingredients-from-meal', MealToIngredientAPIView.as_view(), name='generate-ingredients-from-meal-without-slash'),
]
