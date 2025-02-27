import json
import uuid
from django.core.exceptions import ValidationError
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Message, ChatRoom
from users.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ WebSocket 연결 시 사용자 인증 및 권한 확인 """
        self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        self.room_group_name = f"chat_{self.chatroom_id}"

        # 현재 접속한 사용자 가져오기
        user = self.scope["user"]

        chatroom = await self.get_chatroom(self.chatroom_id)

        # 현재 사용자가 buyer 또는 seller인지 확인
        if user != chatroom.buyer and user != chatroom.seller:
            await self.send(text_data=json.dumps({"error": "접속 권한이 없습니다."}))
            await self.close(code=4003)  # 권한 없음
            return

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
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
            return

        message_content = data.get("message")
        sender = self.scope["user"]  #클라이언트에서 sender_id를 받지 않고 서버에서 인증된 사용자 사용

        if not message_content:
            await self.send(text_data=json.dumps({"error": "Missing message content"}))
            return

        # 숫자 메시지는 문자열로 변환
        if isinstance(message_content, (int, float)):
            message_content = str(message_content)

        # DB에 메시지 저장 (비동기)
        message = await self.save_message(self.chatroom_id, sender, message_content)

        if message is None:
            await self.send(text_data=json.dumps({"error": "Message saving failed"}))
            return

        # WebSocket을 통해 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender_id": str(sender.id),
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
    def get_chatroom(self, chatroom_id):
        """ 채팅방 정보 가져오기 """
        try:
            return ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, chatroom_id, sender, content):
        """ DB에 메시지 저장 (비동기) """
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return None  # 채팅방이 존재하지 않으면 메시지 저장 불가

        message = Message.objects.create(chatRoom=chatroom, sender=sender, content=content)

        # 마지막 메시지 업데이트
        chatroom.update_last_message(message.content, message.time)

        return message


#테스트 로직
#class ChatConsumer(AsyncWebsocketConsumer):
#    async def connect(self):
#        """ WebSocket 연결 """
#        self.chatroom_id = self.scope["url_route"]["kwargs"]["chatroom_id"]
#        self.room_group_name = f"chat_{self.chatroom_id}"
#
#        # WebSocket 그룹에 참가
#        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#        await self.accept()
#
#    async def disconnect(self, close_code):
#        """ WebSocket 연결 종료 """
#        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#
#    async def receive(self, text_data):
#        """ WebSocket을 통해 메시지 수신 후, 같은 채팅방에 있는 모든 클라이언트에게 전송 """
#        try:
#            data = json.loads(text_data)
#            sender_id = data.get("sender_id")  # 숫자 ID 사용 (1 또는 2)
#            message_content = data.get("message")
#
#            if not sender_id or not message_content:
#                return  # 유효하지 않은 데이터 무시
#
#            # ✅ 메시지를 즉시 WebSocket 그룹에 브로드캐스트 (DB 저장 없음)
#            await self.channel_layer.group_send(
#                self.room_group_name,
#                {
#                    "type": "chat_message",
#                    "sender_id": sender_id,
#                    "message": message_content,
#                }
#            )
#
#        except json.JSONDecodeError:
#            pass  # JSON 형식 오류 발생 시 무시
#
#    async def chat_message(self, event):
#        """ WebSocket 그룹 내 모든 사용자에게 메시지 전송 """
#        await self.send(text_data=json.dumps({
#            "sender_id": event["sender_id"],
#            "message": event["message"],
#        }))