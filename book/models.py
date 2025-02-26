from django.db import models
from users.models import User

class Book(models.Model):
    title = models.CharField(max_length=50)  # 책 제목
    author = models.CharField(max_length=50)  # 저자
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 가격
    description = models.TextField(blank=True, null=True)  # 설명
    image = models.ImageField(upload_to='bookpar2/book/', blank=True, null=True)  # 책 이미지
    created_at = models.DateTimeField(auto_now_add=True)  # 등록 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간
    major = models.TextField(max_length=50)  # 전공
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # 사용자 정보
    
    def __str__(self):
        return self.title
    # 유저 추가하기

# Create your models here.
# 데이터 베이스(수납장)을 만드는 공간