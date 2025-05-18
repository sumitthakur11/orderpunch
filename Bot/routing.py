from django.urls import path
from Tradingbot.consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/watchlist/", ChatConsumer.as_asgi()),
    ]

