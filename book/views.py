import io
import boto3
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Book, BookImage
from .serializers import BookSerializer, UserSerializer
from elasticsearch_dsl.query import Bool, MultiMatch
from .search import BookDocument
from django.db.models import Case, When, Value, IntegerField
from uuid import uuid4
import tempfile

# 서적 전체 조회(GET)
class BookListAllView(APIView):
    parser_classes = [AllowAny]  # 파일 업로드를 위한 설정

    def get(self, request, *args, **kwargs):
        """서적 전체 조회 (GET)"""
        books = Book.objects.all().order_by('-created_at')
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

class BookListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 가능

    def post(self, request, *args, **kwargs):
        """서적 등록 기능 (POST)"""
        files = request.FILES.getlist("images")  # 업로드된 파일들 받기
        if not files:
            return Response({"error": "No images uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # S3 클라이언트 설정
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        image_urls = []

        for file in files:
            file_stream = io.BytesIO(file.read())  # 파일을 메모리에서 읽음

            # 파일명 유니크하게 생성
            s3_file_name = f"image/{uuid4()}_{file.name}"

            # S3에 업로드
            s3.upload_fileobj(file_stream, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_file_name)

            # S3 URL 생성
            file_url = f"{settings.MEDIA_URL}{s3_file_name.split('/')[-1]}"
            image_urls.append(file_url)

        # DB에 서적 데이터 저장
        book_data = request.data.copy()
        serializer = BookSerializer(data=book_data)
        if serializer.is_valid():
            book = serializer.save(seller=request.user)  # 현재 로그인한 유저 저장

            # 여러 이미지 저장
            for image_url in image_urls:
                BookImage.objects.create(book=book, image_url=image_url)

            # 책 정보를 포함한 응답 반환
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 유저 별 책 조회(GET)
class BookListByUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """개인 서적 조회 (GET)"""
        books = Book.objects.filter(seller=request.user).annotate(
            for_sale_priority=Case(
                When(status='FOR_SALE', then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            )
        ).order_by('for_sale_priority', '-created_at')  # FOR_SALE이 우선, 최신순 정렬
        book_serializer = BookSerializer(books, many=True)
        sellers = UserSerializer(request.user)
        return Response( {'sellers': sellers.data, 'books': book_serializer.data}, status=status.HTTP_200_OK)  # 200 OK로 응답

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

class BookSearchView(APIView):
    def get(self, request, *args, **kwargs):
        """서적 검색 (GET)"""
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({"error": 'Query parameter "q" is required.'}, status=400)

        # 제목, 저자, 설명, 전공 중 하나라도 검색어와 일치하면 검색
        search_query = Bool(
            should=[
                MultiMatch(query=query, fields=['title']),
                MultiMatch(query=query, fields=['description']),
                MultiMatch(query=query, fields=['major'])
            ],
            minimum_should_match=1  # 하나라도 일치하면 검색됨
        )

        # Elasticsearch 검색 실행
        search = BookDocument.search().query(search_query)
        results = search.execute()

        # 검색된 책 ID 리스트 가져오기
        book_ids = [hit.meta.id for hit in results]

        # DB에서 해당 책 정보 조회
        books = Book.objects.filter(id__in=book_ids)
        serializer = BookSerializer(books, many=True)

        return Response(serializer.data)