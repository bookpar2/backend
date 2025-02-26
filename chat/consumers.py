import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Message, ChatRoom
from users.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        self.room_group_name = f"chat_{self.chatroom_id}"

        #WebSocket 그룹 추가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        #WebSocket 그룹 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """ 메시지를 받으면 DB에 저장 후 브로드캐스트 """
        data = json.loads(text_data)
        sender_id = data.get("sender_id")
        message_content = data.get("message")

        if not sender_id or not message_content:
            return

        # DB에 메시지 저장 (비동기)
        message = await self.save_message(self.chatroom_id, sender_id, message_content)

        # WebSocket을 통해 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender_id": sender_id,
                "message": message.content,
                "time": message.time.strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    async def chat_message(self, event):
        """ 모든 클라이언트에게 메시지 전달 """
        await self.send(text_data=json.dumps({
            "sender_id": event["sender_id"],
            "message": event["message"],
            "time": event["time"]
        }))

    @sync_to_async
    def save_message(self, chatroom_id, sender_id, content):
        """ DB에 메시지 저장 (비동기) """
        sender = User.objects.get(id=sender_id)
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        message = Message.objects.create(chatRoom=chatroom, sender=sender, content=content)

        # 마지막 메시지 업데이트
        chatroom.update_last_message(message.content, message.time)

        return message