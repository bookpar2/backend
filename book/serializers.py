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

class BookUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    existing_images = BookImageSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['title', 'chatLink', 'price', 'description', 'major', 'status', 'images', 'existing_images']

    def update(self, instance, validated_data):
        # 새로 보낸 이미지 배열 추출
        new_images = validated_data.pop('images', None)

        # 나머지 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 이미지 교체 처리
        if new_images is not None:
            instance.images.all().delete()  # 기존 이미지 삭제
            for url in new_images:
                BookImage.objects.create(book=instance, image_url=url)

        return instance

class UserSerializer(serializers.ModelSerializer):
    """User 정보 직렬화"""
    class Meta:
        model = User
        fields = ['name', 'student_id', 'school_email']