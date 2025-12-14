# filters.py
import django_filters
from .models import Meal

class MealFilter(django_filters.FilterSet):
    meal_name = django_filters.CharFilter(
        field_name="meal_name",
        lookup_expr="iexact"   # exact match, case-insensitive
    )

    class Meta:
        model = Meal
        fields = ["meal_name"]
