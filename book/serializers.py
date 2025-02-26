# from rest_framework import serializers
# from .models import Book

# class BookSerializer(serializers.ModelSerializer):
#     """Book 모델을 위한 Serializer"""
    
#     # 이미지를 선택적으로 받기 위한 설정
#     image = serializers.ImageField(required=False, allow_null=True)
    
#     # 이미지 URL을 반환하기 위한 필드
#     image_url = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Book
#         fields = [
#             'id', 'title', 'author', 'price', 'description', 
#             'image', 'image_url', 'major', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['created_at', 'updated_at', 'image_url']
    
#     def get_image_url(self, obj):
#         """이미지 URL을 반환"""
#         if obj.image:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(obj.image.url)
#             return obj.image.url
#         return None
    
#     def validate_price(self, value):
#         """가격 유효성 검사"""
#         if value < 0:
#             raise serializers.ValidationError("가격은 0 이상이어야 합니다.")
#         return value
    
#     def validate_title(self, value):
#         """제목 유효성 검사"""
#         if len(value) < 2:
#             raise serializers.ValidationError("제목은 최소 2자 이상이어야 합니다.")
#         return value
    
#     def validate_author(self, value):
#         """저자 유효성 검사"""
#         if len(value) < 2:
#             raise serializers.ValidationError("저자 이름은 최소 2자 이상이어야 합니다.")
#         return value
    
#     def to_representation(self, instance):
#         """응답 데이터 형식 수정"""
#         representation = super().to_representation(instance)
        
#         # 가격에 천 단위 구분기호 추가
#         representation['formatted_price'] = f"{instance.price:,}원"
        
#         # 등록일/수정일 형식 변경
#         if instance.created_at:
#             representation['created_at'] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
#         if instance.updated_at:
#             representation['updated_at'] = instance.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        
#         return representation

from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'description', 'major', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']