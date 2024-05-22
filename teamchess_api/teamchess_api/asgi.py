"""
ASGI config for teamchess_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator
from room.routing import websocket_urlpatterns as room_websocket_urlpatterns


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teamchess_api.settings')

asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': asgi_app,
    'websocket': AllowedHostsOriginValidator(room_websocket_urlpatterns),
})
