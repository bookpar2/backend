from django.apps import AppConfig
from elasticsearch_dsl import connections

class BookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'book'

    def ready(self):
        connections.create_connection(hosts=["http://localhost:9200"])
        from book.signals import index_existing_books
        index_existing_books()