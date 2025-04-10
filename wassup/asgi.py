"""
ASGI config for wassup project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wassup.settings')

# Load the HTTP application
django_asgi_app = get_asgi_application()

# Import routing after Django is ready
import django
django.setup()
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # Handle traditional HTTP requests with Django
    "http": django_asgi_app,
    # Handle WebSocket requests with Channels
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
