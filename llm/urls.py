from django.urls import path
from .views import MealToIngredientAPIView

urlpatterns = [
    path('generate-ingredients-from-meal/', MealToIngredientAPIView.as_view()),
]
