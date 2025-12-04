from django.urls import path
from .consumers import TestConsumer

websocket_urlpatterns = [
    path("ws/test/", TestConsumer.as_asgi()),
]
