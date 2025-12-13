from django.shortcuts import render
import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from foods.models import Ingredient, FoodGroup, Nutrient
from meals.models import Meal   # <<< ADD THIS
from .extract_ingredients import extract_ingredients_from_meal

FOOD_GROUPS = {
    "Whole Grains": "全穀雜糧類",
    "Beans/Fish/Egg/Meat": "豆魚蛋肉類",
    "Vegetables": "蔬菜類",
    "Fruits": "水果類",
    "Dairy Product": "乳品類",
    "Nuts and Seeds": "堅果種子類",
    "Condiments/Seasonings": "調味品類"
}


class MealToIngredientAPIView(APIView):
    def post(self, request):
        meal_name = request.data.get("meal_name")  # unique identifier for the meal
        meal_text = request.data.get("meal")  # optional description
        meal_time = request.data.get("meal_time")  # optional
        day_cycle = request.data.get("day_cycle")  # optional
        plate_type = request.data.get("plate_type")  # optional
        meal_image = request.FILES.get("image")  # handle uploaded image

        if not meal_name:
            return Response({"error": "Meal name is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Use meal_name as default description if meal text not provided
        if not meal_text:
            meal_text = meal_name

        try:
            created_ingredients = []
            ingredient_ids = []

            # --- Extract ingredients as before ---
            if meal_text:
                data = extract_ingredients_from_meal(meal_text)
                # save JSON for debugging
                json_path = os.path.join(os.path.dirname(__file__), "extracted_ingredients.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                existing_ingredients = Ingredient.objects.values_list('name', flat=True)
                existing_ingredients = [name.lower() for name in existing_ingredients]

                for item in data.get("ingredients", []):
                    name_lower = item["name"].lower()
                    food_group_name = item["food_group"]
                    try:
                        fg = FoodGroup.objects.get(name=food_group_name)
                    except FoodGroup.DoesNotExist:
                        return Response(
                            {"error": f"Invalid food group: {food_group_name}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    nutrient_ids = []
                    for n in item.get("nutrients", []):
                        nut, _ = Nutrient.objects.get_or_create(name=n)
                        nutrient_ids.append(nut)

                    ingredient, created_flag = Ingredient.objects.get_or_create(name=item["name"])
                    if ingredient.food_group is None:
                        ingredient.food_group = fg
                    ingredient.nutrients.set(nutrient_ids)
                    ingredient.save()

                    ingredient_ids.append(ingredient.id)

                    created_ingredients.append({
                        "name": ingredient.name,
                        "food_group": ingredient.food_group.name,
                        "nutrients": [nut.name for nut in ingredient.nutrients.all()],
                        "created": created_flag
                    })

            # --- Create or update meal ---
            meal, created = Meal.objects.get_or_create(
                meal_name=meal_name,
                defaults={
                    "meal_description": meal_text,
                    "meal_time": meal_time,
                    "day_cycle": day_cycle,
                    "plate_type": plate_type,
                    "image": meal_image
                }
            )

            updated = False
            if not created:
                if meal.meal_description != meal_text or \
                   meal.meal_time != meal_time or \
                   meal.day_cycle != day_cycle or \
                   meal.plate_type != plate_type or \
                   (meal_image is not None):
                    meal.meal_description = meal_text
                    meal.meal_time = meal_time or meal.meal_time
                    meal.day_cycle = day_cycle or meal.day_cycle
                    meal.plate_type = plate_type or meal.plate_type
                    if meal_image is not None:
                        meal.image = meal_image
                    updated = True

            if ingredient_ids:
                current_ingredient_ids = set(meal.ingredients.values_list('id', flat=True))
                new_ingredient_ids = set(ingredient_ids)
                if current_ingredient_ids != new_ingredient_ids:
                    meal.ingredients.set(ingredient_ids)
                    updated = True

            if updated:
                meal.save()

            meal_data = {
                "id": meal.id,
                "meal_name": meal.meal_name,
                "meal_time": meal.meal_time,
                "day_cycle": meal.day_cycle,
                "meal_description": meal.meal_description,
                "plate_type": meal.plate_type,
                "image": meal.image.url if meal.image else None,
                "ingredients": list(meal.ingredients.values_list('id', flat=True)),
                "created": created,
                "updated": updated
            }

            return Response({
                "ingredients": created_ingredients,
                "meal": meal_data
            })

        except Exception as e:
            print("General error:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
