from django.db import models
from users.models import User  # User 모델 직접 불러오기
from book.models import Book

class ChatRoom(models.Model):
    buyer = models.ForeignKey(User, related_name='chat_buyer', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='chat_book', on_delete=models.CASCADE)
    last_message = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey(User, related_name='chat_seller', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['buyer', 'book'], name='unique_chatroom_per_buyer_book')
        ]

    def update_last_message(self, content, time):
        """ 마지막 메시지를 업데이트하는 메서드 (DB 트랜잭션 최소화) """
        self.last_message = content
        self.updated_at = time
        self.save(update_fields=['last_message', 'updated_at'])

class Message(models.Model):
    chatRoom = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.chatRoom.last_message = self.content
        self.chatRoom.updated_at = self.time
        self.chatRoom.save()

    class Meta:
        db_table = 'Message'
