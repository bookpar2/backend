from rest_framework import serializers
from .models import Book
from users.models import User

class BookSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    image = serializers.ImageField(use_url=True, required=False)  # 변경: 이미지 URL이 아니라 파일 필드 사용
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'chatLink', 'price', 'description', 'image', 'major', 'status', 'created_at', 'updated_at', 'seller', 'seller_name']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    """User 정보 직렬화"""
    class Meta:
        model = User
        fields = ['name', 'student_id', 'school_email']