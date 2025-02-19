from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path(r'ws/<int:room_id>/', ChatConsumer.as_asgi()),
]
