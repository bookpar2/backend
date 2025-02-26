from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'description', 'image', 'image_url', 'major', 'created_at', 'updated_at', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url']

    def get_image_url(self, obj):
        """이미지 URL을 반환"""
        if obj.image:
            return obj.image.url
        return None