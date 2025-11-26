from django.db import models

class Patient(models.Model):
    # --- Personal Information ---
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=10, choices=[('male','Male'),('female','Female')], null=True, blank=True)
    height_cm = models.FloatField()
    weight_kg = models.FloatField()
    
    # --- Medical Data ---
    heart_rate = models.PositiveIntegerField(null=True, blank=True)
    systolic_bp = models.PositiveIntegerField(null=True, blank=True)
    diastolic_bp = models.PositiveIntegerField(null=True, blank=True)

    # --- Metadata ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- Activity ---
    ACTIVITY_LEVEL_CHOICES = [
        ('inactive', 'Inactive'),
        ('low_active', 'Low Active'),
        ('active', 'Active'),
        ('very_active', 'Very Active'),
    ]
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='inactive')

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 2)
        return None

    def __str__(self):
        return self.name

