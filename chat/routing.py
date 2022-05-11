from django.urls import path

from chat.consumers import ChatConsumer

ws_url_patterns = [
    path("ws/chat/", ChatConsumer.as_asgi()),
]