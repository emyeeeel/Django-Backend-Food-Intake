from django.db import models

class FoodGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Nutrient(models.Model):
    """Represents a nutrient category (e.g., Protein, Carbs, Fat)"""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    
    # Link to food group
    food_group = models.ForeignKey(
        FoodGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ingredients'
    )

    # Link to nutrients (categories only)
    nutrients = models.ManyToManyField(
        Nutrient,
        related_name='ingredients',
        blank=True
    )

    image = models.ImageField(upload_to="ingredients/", null=True, blank=True)

    def __str__(self):
        return self.name
