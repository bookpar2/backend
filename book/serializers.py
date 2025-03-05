from rest_framework import serializers
from .models import Book, BookImage
from users.models import User

class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ['image_url']
        extra_kwargs = {
            'image_url': {'required': False}
        }

class BookSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    images = BookImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'chatLink', 'price', 'description', 'major', 'status', 'created_at', 'updated_at', 'seller', 'seller_name', 'images']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    """User 정보 직렬화"""
    class Meta:
        model = User
        fields = ['name', 'student_id', 'school_email']