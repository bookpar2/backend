from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book
from .search import BookDocument

@receiver(post_save, sender=Book)
def index_book(sender, instance, **kwargs):
    # Elasticsearch 인덱스를 자동으로 생성
    BookDocument.init()

    # 새로운 데이터가 인덱스에 추가되도록
    book_document = BookDocument()
    book_document.update(instance)

# 기존 데이터들을 인덱스에 추가하도록 설정
def index_existing_books():
    for book in Book.objects.all():
        BookDocument().update(book)