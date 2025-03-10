from rest_framework import serializers
from .models import Book, BookImage
from users.models import User

class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ['image_url']

class BookSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    images = BookImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'chatLink', 'price', 'description', 'major', 'status', 'created_at', 'updated_at', 'seller', 'seller_name', 'images']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'chatLink', 'price', 'description', 'major', 'status', 'seller']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        images = validated_data.pop('images', [])  # images 필드를 추출
        book = Book.objects.create(**validated_data)  # Book 객체 생성

        # BookImage 모델에 각 이미지 URL을 저장
        for image_url in images:
            BookImage.objects.create(book=book, image_url=image_url)

        return book

class UserSerializer(serializers.ModelSerializer):
    """User 정보 직렬화"""
    class Meta:
        model = User
        fields = ['name', 'student_id', 'school_email']