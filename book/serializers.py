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
    images = BookImageSerializer(many=True, read_only=True)  # 기존 이미지 조회용
    new_images = serializers.ListField(
        child=serializers.CharField(),  # URL 형태로 전달한다고 가정
        write_only=True,
        required=False
    )

    class Meta:
        model = Book
        fields = ['title', 'chatLink', 'price', 'description', 'major', 'status', 'images', 'new_images']

    def update(self, instance, validated_data):
        new_images = validated_data.pop('new_images', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if new_images is not None:
            instance.images.all().delete()  # 기존 이미지 삭제
            for image_url in new_images:
                BookImage.objects.create(book=instance, image_url=image_url)

        return instance

class UserSerializer(serializers.ModelSerializer):
    """User 정보 직렬화"""
    class Meta:
        model = User
        fields = ['name', 'student_id', 'school_email']