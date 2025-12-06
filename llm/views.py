from django.shortcuts import render

# Create your views here.
import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from foods.models import Ingredient, FoodGroup, Nutrient
from .extract_ingredients import extract_ingredients_from_meal


class MealToIngredientAPIView(APIView):
    def post(self, request):
        meal = request.data.get("meal")
        if not meal:
            return Response({"error": "Meal parameter is required"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            # The extract_ingredients_from_meal function returns a dict, not a string
            data = extract_ingredients_from_meal(meal)  # Remove json.loads() here


            # Save JSON
            json_path = os.path.join(os.path.dirname(__file__), "extracted_ingredients.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)


            # Fetch existing ingredients from DB
            existing_ingredients = Ingredient.objects.values_list('name', flat=True)
            existing_ingredients = [name.lower() for name in existing_ingredients]


            created = []


            # Process ingredients
            for item in data.get("ingredients", []):
                name_lower = item["name"].lower()
                if name_lower in existing_ingredients:
                    print(f"{item['name']} already exists, skipping creation.")
                    continue  # Skip existing


                fg, _ = FoodGroup.objects.get_or_create(name=item["food_group"])
                nutrient_ids = []
                for n in item["nutrients"]:
                    nut, _ = Nutrient.objects.get_or_create(name=n)
                    nutrient_ids.append(nut)


                ingredient, _ = Ingredient.objects.get_or_create(
                    name=item["name"],
                    defaults={"food_group": fg}
                )
                ingredient.nutrients.set(nutrient_ids)
                ingredient.save()


                created.append({
                    "name": ingredient.name,
                    "food_group": ingredient.food_group.name,
                    "nutrients": [nut.name for nut in ingredient.nutrients.all()]
                })


        except json.JSONDecodeError:
            return Response({"error": "Failed to parse LLM response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except KeyError as e:
            return Response({"error": f"Missing required field in LLM response: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"General error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return Response({"ingredients": created})