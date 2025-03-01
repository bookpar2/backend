from django_elasticsearch_dsl import Document, fields
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry
from .models import Book

@registry.register_document
class BookDocument(Document):
    title = fields.TextField(analyzer='edge_ngram_analyzer')
    author = fields.TextField(analyzer='edge_ngram_analyzer')
    description = fields.TextField(analyzer='edge_ngram_analyzer')
    major = fields.TextField(analyzer='edge_ngram_analyzer')

    class Index:
        name = 'books'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            # edge_ngram 분석기 추가
            'analysis': {
                'tokenizer': {
                    'edge_ngram_tokenizer': {
                        'type': 'edge_ngram',
                        'min_gram': 2,
                        'max_gram': 25,
                        'token_chars': ['letter', 'digit']
                    }
                },
                'analyzer': {
                    'edge_ngram_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'edge_ngram_tokenizer',
                    }
                }
            }
        }

    class Django:
        model = Book