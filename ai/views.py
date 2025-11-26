import pickle
import numpy as np
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from patients.models import Patient
from django.conf import settings
import os


class RecommendedIntakeDetail(APIView):

    def get(self, request, patient_id):
        try:
            # Retrieve patient
            patient = Patient.objects.get(id=patient_id)

            # Load model
            model_path = os.path.join(settings.BASE_DIR, 'ai', 'models', 'multi_output_catboost.pkl')
            with open(model_path, "rb") as f:
                model = pickle.load(f)

            # Load label encoders
            enc_path = os.path.join(settings.BASE_DIR, 'ai', 'models', 'label_encoders.pkl')
            with open(enc_path, "rb") as f:
                label_encoders = pickle.load(f)

            # Inspect the label encoder for 'activity_level'
            # print(label_encoders['activity_level'].classes_)

            # Prepare Input DataFrame
            input_df = self._prepare_input_dataframe(patient)

            # Apply the same encoders used during training
            input_df = self._apply_saved_encoders(input_df, label_encoders)

            # Predict
            prediction = model.predict(input_df)[0]

            # Format prediction output
            response_data = self._format_prediction(prediction, patient, input_df)

            return Response(response_data, status=status.HTTP_200_OK)

        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"Prediction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ---------------------------- PREPROCESSING ---------------------------- #

    def _prepare_input_dataframe(self, patient):
        """Prepare input features identical to training."""
        
        activity_mapping = {
            'inactive': 'Inactive',
            'low_active': 'Low Active',
            'active': 'Active',
            'very_active': 'Very Active',
        }

        sex_mapping = {
            'male': 'Male',
            'female': 'Female'
        }

        return pd.DataFrame({
            "sex": [sex_mapping.get(patient.sex, "Male")],
            "age": [patient.age],
            "height": [patient.height_cm],
            "weight": [patient.weight_kg],
            "activity_level": [activity_mapping.get(patient.activity_level, "Active")],
            "bmi": [patient.bmi]   
        })

    def _apply_saved_encoders(self, df, encoders):
        """Apply the saved label encoders from training."""
        df = df.copy()
        for col, encoder in encoders.items():
            df[col] = encoder.transform(df[col])
        return df

    # --------------------------- FORMAT OUTPUT ----------------------------- #

    def _format_prediction(self, prediction, patient, input_df):

        output_cols = [
            "daily_caloric_needs",
            "carbohydrate",
            "total_fiber",
            "protein",
            "fat",
            "alpha_linolenic_acid",
            "linoleic_acid",
            "total_water"
        ]

        formatted = {}
        for label, value in zip(output_cols, prediction):
            value = float(value)

            # Rounding rules
            if label == "daily_caloric_needs":
                formatted[label] = round(value, 0)
            elif label in ["carbohydrate", "total_fiber", "protein", "fat"]:
                formatted[label] = round(value, 1)
            else:
                formatted[label] = round(value, 3)

        return {
            "patient_id": patient.id,
            "patient_name": patient.name,
            
            "patient_info": {
                "sex": patient.sex,
                "age": patient.age,
                "height_cm": patient.height_cm,
                "weight_kg": patient.weight_kg,
                "activity_level": patient.activity_level,
                "bmi": round(input_df["bmi"].iloc[0], 2)
            },

            "nutritional_recommendations": formatted,

            "units": {
                "daily_caloric_needs": "kcal",
                "carbohydrate": "g",
                "total_fiber": "g",
                "protein": "g",
                "fat": "g",
                "alpha_linolenic_acid": "g",
                "linoleic_acid": "g",
                "total_water": "L"
            }
        }
