from rest_framework.viewsets import ModelViewSet
from patients.models import Patient
from patients.serializers import PatientSerializer


class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.order_by('-created_at')
    serializer_class = PatientSerializer
