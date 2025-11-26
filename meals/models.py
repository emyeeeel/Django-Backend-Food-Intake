from django.db import models
from foods.models import Ingredient
from patients.models import Patient


class Meal(models.Model):

    MEAL_TIME_CHOICES = (
        ('午餐', 'Lunch'),
        ('晚餐', 'Dinner'),
        ('點心', 'Snack'),
    )

    DAY_CYCLE_CHOICES = [(i, f'Day {i}') for i in range(1, 15)]  # Day 1 - Day 14

    PLATE_TYPE_CHOICES = (
        ('金属板', 'Metal Plate'),
        ('金属碗', 'Metal Bowl'),
        ('陶瓷碗', 'Ceramic Bowl'),
    )

    meal_time = models.CharField(
        max_length=20,
        choices=MEAL_TIME_CHOICES,
        null=True,
        blank=True,
    )

    day_cycle = models.CharField(
        max_length=10,
        choices=DAY_CYCLE_CHOICES,
        null=True,
        blank=True,
    )

    meal_description = models.CharField(max_length=255)

    plate_type = models.CharField(
        max_length=50,
        choices=PLATE_TYPE_CHOICES,
        null=True,
        blank=True,
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="meals",
        blank=True
    )

    image = models.ImageField(
        upload_to="meals/", 
        null=True, 
        blank=True
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.meal_description} ({self.meal_time}, {self.day_cycle})"
    

class MealAssignment(models.Model):
    patient = models.ForeignKey(
        Patient,  # Use the actual model class
        on_delete=models.CASCADE,
        related_name='meal_assignments'
    )
    meal = models.ForeignKey(
        'Meal',  # same app
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    meal_type = models.CharField(
        max_length=10,
        choices=(
            ('lunch', 'Lunch'),
            ('dinner', 'Dinner'),
            ('snack', 'Snack'),
        )
    )
    day_cycle = models.PositiveSmallIntegerField()  # Day number, e.g., 1-14

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'meal_type', 'day_cycle')  # One meal type per day per patient

    def __str__(self):
        return f"{self.patient.name} - {self.meal_type} Day {self.day_cycle}"