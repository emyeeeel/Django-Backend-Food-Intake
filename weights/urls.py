from django.urls import path
from . import views

urlpatterns = [
    path('receive-raw/', views.receive_raw, name='receive_raw'),
    path('select-container/', views.select_container, name='select_container'),
    path('get-net-weight/', views.get_net_weight, name='get_net_weight'),
]