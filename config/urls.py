# """
# URL configuration for config project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
from django.contrib import admin
from django.urls import path, include
from book.views import BookListCreateView, BookDetailView, BookListByUser, BookSearchView, BookListAllView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/books/all', BookListAllView.as_view(), name='all-book-list'),
    path('api/v1/books/', BookListCreateView.as_view(), name='book-list-create'),
    path('api/v1/books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('api/v1/books/user/', BookListByUser.as_view(), name='book-by-user'),
    path('api/v1/search/', BookSearchView.as_view(), name='search_books'),
    path('api/v1/users/', include('users.urls')),
    path('', include('chat.urls')),
]