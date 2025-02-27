# from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.filters import SearchFilter
# from django.db.models import Q
# from .models import Book
# from .serializers import BookSerializer

# # 서적 전체 조회(GET) 및 서적 등록(POST)
# class BookListCreateView(generics.ListCreateAPIView):
#     queryset = Book.objects.all().order_by('-created_at')
#     serializer_class = BookSerializer
#     filter_backends = [SearchFilter]
#     search_fields = ['title', 'author', 'major']
    
#     def post(self, request, *args, **kwargs):
#         """서적 등록 기능 (POST)"""
#         return self.create(request, *args, **kwargs)

# # 서적 제목 검색 (GET)
# class BookSearchView(generics.ListAPIView):
#     serializer_class = BookSerializer
    
#     def get_queryset(self):
#         """서적 제목으로 검색"""
#         query = self.request.query_params.get('title', '')
#         if query:
#             return Book.objects.filter(title__icontains=query).order_by('-created_at')
#         return Book.objects.none()

# # 특정 책 조회(GET), 수정(PATCH), 삭제(DELETE)
# class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer
    
#     def get(self, request, *args, **kwargs):
#         """개별 서적 조회 (GET)"""
#         return self.retrieve(request, *args, **kwargs)
    
#     def patch(self, request, *args, **kwargs):
#         """개별 서적 수정 (PATCH)"""
#         return self.partial_update(request, *args, **kwargs)
    
#     def delete(self, request, *args, **kwargs):
#         """개별 서적 삭제 (DELETE)"""
#         return self.destroy(request, *args, **kwargs)
    
#     # PUT 메서드 사용 비활성화 (PATCH만 사용)
#     def put(self, request, *args, **kwargs):
#         return Response(
#             {"detail": "PUT 메서드는 지원하지 않습니다. PATCH를 사용하세요."}, 
#             status=status.HTTP_405_METHOD_NOT_ALLOWED
#         )

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Book
from .serializers import BookSerializer

# 서적 전체 조회(GET) 및 서적 등록(POST) 
class BookListCreateView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 유저만 서적 등록 가능

    def get(self, request, *args, **kwargs):
        """서적 전체 조회 (GET)"""
        books = Book.objects.all().order_by('-created_at')
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """서적 등록 기능 (POST)"""
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            # 유저 정보 자동으로 추가 (현재 로그인한 유저)
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 유저 별 책 조회(GET)
class BookListByUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """개인 서적 조회 (GET)"""
        books = Book.objects.filter(seller=request.user).order_by('-created_at')
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # 200 OK로 응답

# 특정 책 조회(GET), 수정(PATCH), 삭제(DELETE)
class BookDetailView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 유저만 수정/삭제 가능

    def get(self, request, *args, **kwargs):
        """개별 서적 조회 (GET)"""
        book = Book.objects.get(pk=kwargs['pk'])
        serializer = BookSerializer(book)
        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        """개별 서적 수정 (PATCH)"""
        book = Book.objects.get(pk=kwargs['pk'])
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        """개별 서적 삭제 (DELETE)"""
        book = Book.objects.get(pk=kwargs['pk'])
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)