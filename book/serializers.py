from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'description', 'image_url', 'major', 'status', 'created_at', 'updated_at', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at']