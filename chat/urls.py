from django.urls import path
from .views import websocket_test, create_chatroom, get_chatroom_messages, get_chatrooms

urlpatterns = [
    path("test-websocket", websocket_test, name="websocket_test"),
    path("api/v1/chatroom", create_chatroom, name="create_chatroom"),
    path("api/v1/chatroom/<int:chatroom_id>/messages", get_chatroom_messages, name="get_chatroom_messages"),
    path("api/v1/chatrooms", get_chatrooms, name="get_chatrooms")
]
