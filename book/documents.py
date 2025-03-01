# from django_elasticsearch_dsl import Document, fields
# from django_elasticsearch_dsl.registries import registry
# from .models import Book

# @registry.register_document
# class BookDocument(Document):
#     title = fields.TextField(analyzer='edge_ngram_analyzer')  # 이 필드에 분석기 적용

#     class Index:
#         name = 'books'
#         settings = {
#             'number_of_shards': 1,
#             'number_of_replicas': 0,
#             'analysis': {
#                 'tokenizer': {
#                     'edge_ngram_tokenizer': {
#                         'type': 'edge_ngram',
#                         'min_gram': 2,
#                         'max_gram': 25,
#                         'token_chars': ['letter', 'digit']
#                     }
#                 },
#                 'analyzer': {
#                     'edge_ngram_analyzer': {
#                         'type': 'custom',
#                         'tokenizer': 'edge_ngram_tokenizer',
#                     }
#                 }
#             }
#         }

#     class Django:
#         model = Book