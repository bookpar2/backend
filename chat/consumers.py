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

        # 현재 사용자가 buyer 또는 seller인지 확인
        if user not in [chatroom.buyer, chatroom.seller]:
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

        sender_id = data.get("sender_id")
        message_content = data.get("message")

        if not sender_id or message_content is None:
            await self.send(text_data=json.dumps({"error": "Missing sender_id or message"}))
            return

        # 숫자 메시지는 문자열로 변환
        if isinstance(message_content, (int, float)):
            message_content = str(message_content)

        # sender_id가 문자열인 경우 UUID 변환 (안전하게 처리)
        try:
            sender_id = uuid.UUID(sender_id) if isinstance(sender_id, str) else sender_id
        except ValueError:
            await self.send(text_data=json.dumps({"error": "잘못된 sender_id 형식입니다."}))
            return

        # DB에 메시지 저장 (비동기)
        message = await self.save_message(self.chatroom_id, sender_id, message_content)

        # WebSocket을 통해 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender_id": str(sender_id),  # UUID를 문자열로 변환하여 보냄
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
        try:
            # sender_id가 UUID인 경우 변환
            sender_uuid = uuid.UUID(sender_id) if isinstance(sender_id, str) else sender_id
            sender = User.objects.get(id=sender_uuid)
        except (ValueError, ValidationError, User.DoesNotExist):
            return None  # 존재하지 않는 유저 예외 처리

        chatroom = ChatRoom.objects.get(id=chatroom_id)
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