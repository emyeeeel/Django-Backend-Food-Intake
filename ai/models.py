from django.db import models
from patients.models import Patient

class RecommendedIntake(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='recommended_intake')
    daily_caloric_needs = models.FloatField()
    carbohydrate = models.FloatField()
    total_fiber = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    saturated_fatty_acids = models.FloatField()
    trans_fatty_acids = models.FloatField()
    alpha_linolenic_acid = models.FloatField()
    linoleic_acid = models.FloatField()
    dietary_cholesterol = models.FloatField()
    total_water = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recommended Intake for {self.patient.name}"
