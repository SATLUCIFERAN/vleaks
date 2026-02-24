
# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('blog/categories/', views.category_list, name='category_list'),
    path('blog/category/<slug:slug>/', views.category_articles, name='category_articles'),
    # ← ADD THIS!
    path('blog/author/<str:username>/', views.author_articles, name='author_articles'),  
]


