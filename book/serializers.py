from rest_framework import serializers
from .models import Book
from users.models import User

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'chatLink', 'price', 'description', 'image_url', 'major', 'status', 'created_at', 'updated_at', 'seller']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    """User 정보 직렬화"""
    class Meta:
        model = User
        fields = ['name', 'student_id', 'school_email']