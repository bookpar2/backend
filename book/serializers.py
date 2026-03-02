from rest_framework import serializers
from .models import Book, BookImage
from users.models import User

class BookSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    
    # PATCH에서 쓰기 가능하도록 images 필드 설정
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'chatLink', 'price', 'description', 'major', 'status',
            'created_at', 'updated_at', 'seller', 'seller_name', 'images'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)

        # 나머지 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 이미지 교체 처리
        if images_data:
            # 기존 이미지 삭제
            instance.images.all().delete()

            # S3 업로드
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            for file in images_data:
                file_stream = io.BytesIO(file.read())
                file_stream.seek(0)
                s3_file_name = f"image/{uuid4()}_{file.name}"
                s3.upload_fileobj(file_stream, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_file_name)
                
                file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_file_name}"
                BookImage.objects.create(book=instance, image_url=file_url)

        return instance
        
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