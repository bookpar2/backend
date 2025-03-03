from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Book

@registry.register_document
class BookDocument(Document):
    title = fields.TextField(analyzer='edge_ngram_analyzer', search_analyzer='edge_ngram_analyzer')
    description = fields.TextField(analyzer='edge_ngram_analyzer', search_analyzer='edge_ngram_analyzer')
    major = fields.TextField(analyzer='edge_ngram_analyzer', search_analyzer='edge_ngram_analyzer')

    class Index:
        name = 'books'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'tokenizer': {
                    'edge_ngram_tokenizer': {
                        'type': 'edge_ngram',
                        'min_gram': 1,
                        'max_gram': 25,
                        'token_chars': ['letter', 'digit']
                    }
                },
                'filter': {
                    'word_delimiter_filter': {
                        'type': 'word_delimiter',
                        'preserve_original': True,
                        'split_on_case_change': True,
                        'split_on_numerics': True
                    }
                },
                'analyzer': {
                    'edge_ngram_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'edge_ngram_tokenizer'
                    }
                }
            }
        }

    class Django:
        model = Book  # Book 모델을 연결