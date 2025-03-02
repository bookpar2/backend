from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book
from .search import BookDocument

# 새로운 책이 저장될 때마다 Elasticsearch에 인덱싱
@receiver(post_save, sender=Book)
def index_book(sender, instance, created, **kwargs):
    if created:
        book_document = BookDocument()
        book_document.update(instance)

# 기존 데이터들을 Elasticsearch에 추가하도록 설정
def index_existing_books():
    for book in Book.objects.all():
        book_document = BookDocument()
        book_document.update(book)