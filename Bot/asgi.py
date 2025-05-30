"""
ASGI config for Bot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bot.settings")
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from  Bot.routing  import websocket_urlpatterns

print(websocket_urlpatterns)


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bot.settings')

# application = get_asgi_application()
