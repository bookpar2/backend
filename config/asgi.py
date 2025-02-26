"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns  # WebSocket URL 라우팅 추가

# Django 설정 모듈을 환경 변수로 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# ASGI 애플리케이션 설정
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP 요청 처리
    "websocket": AuthMiddlewareStack(  # WebSocket 요청 처리
        URLRouter(
            websocket_urlpatterns  # WebSocket URL을 Django에 연결
        )
    ),
})