import os
import json
import re
from groq import Groq


def extract_ingredients_from_meal(meal_name: str):
    # Get API key from environment variable
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
   
    # Initialize Groq client
    client = Groq(api_key=api_key)
   
    # Create detailed prompt for ingredient extraction
    prompt = f"""
    You are a professional nutrition expert. Analyze the meal: "{meal_name}" and extract ALL individual ingredients.

    For each ingredient, provide:
    1. "name": The exact ingredient name (no cooking methods, no descriptors)
    2. "food_group": Choose ONLY from these 7 categories:
    - "全穀雜糧類" (Whole Grains: rice, bread, pasta, quinoa, oats)
    - "豆魚蛋肉類" (Beans/Fish/Egg/Meat: tofu, chicken, beef, fish, beans, eggs)
    - "蔬菜類" (Vegetables: all vegetables including leafy greens, root vegetables)
    - "水果類" (Fruits: all fresh and dried fruits)
    - "乳品類" (Dairy Product: milk, cheese, yogurt, butter)
    - "堅果種子類" (Nuts and Seeds: almonds, peanuts, sesame seeds)
    - "調味品類" (Condiments/Seasonings: soy sauce, salt, sugar, oil, vinegar, spices, herbs)

    3. "nutrients": Choose from these 5 nutrients based on what the ingredient naturally contains:
    - "Carbohydrate" (grains, fruits, some vegetables)
    - "Protein" (meat, fish, beans, eggs, dairy)
    - "Fats" (oils, nuts, meat, dairy)
    - "Water" (vegetables, fruits)
    - "Total Fiber" (vegetables, fruits, whole grains)

    IMPORTANT RULES:
    - Break down complex dishes into individual components
    - Condiments like soy sauce, vinegar, oil are "調味品類"
    - If an ingredient has no significant nutrients, use empty array []
    - Use standardized ingredient names (e.g., "scallion" not "green onion")
    - Do NOT include cooking methods as ingredients
    - Do NOT invent new food groups; only use the 7 listed above

    Return ONLY valid JSON in this exact format:
    {{
        "ingredients": [
            {{
                "name": "ingredient_name",
                "food_group": "category",
                "nutrients": ["nutrient1", "nutrient2"]
            }}
        ]
    }}
    """

   
    try:
        # Make API call to Groq
        response = client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}],
        )
       
        raw_output = response.choices[0].message.content
       
        # Clean and extract JSON from the response
        if raw_output:
            # Try to find JSON pattern in the response
            json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # Parse JSON to validate it
                parsed_json = json.loads(json_str)
                return parsed_json
            else:
                # Fallback: return empty ingredients if no JSON found
                return {"ingredients": []}
        else:
            return {"ingredients": []}
           
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {raw_output}")
        return {"ingredients": []}
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return {"ingredients": []}