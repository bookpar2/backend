from django.db import models
from users.models import User

class Book(models.Model):
    STATUS_CHOICES = [
        ('FOR_SALE', '판매 중'),
        ('IN_PROGRESS', '거래 중'),
        ('COMPLETED', '거래 완료'),
    ]

    title = models.CharField(max_length=50)  # 책 제목
    chatLink = models.TextField(max_length=500)  # 오픈채팅 링크
    price = models.IntegerField()  # 가격
    description = models.TextField(blank=True, null=True)  # 설명
    image_url = models.URLField(max_length=500, blank=True, null=True)  #URL 저장 방식으로 변경
    major = models.CharField(max_length=50)  # 전공
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FOR_SALE')  # 거래 상태
    created_at = models.DateTimeField(auto_now_add=True)  # 등록 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # 사용자 정보

    def __str__(self):
        return self.title

# Create your models here.
# 데이터 베이스(수납장)을 만드는 공간