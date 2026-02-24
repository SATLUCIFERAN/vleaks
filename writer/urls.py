
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='writer_dashboard'),
    path('login/', views.writer_login, name='writer_login'),
    path('register/', views.writer_register, name='writer_register'),
    path('logout/', views.writer_logout, name='writer_logout'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('create/', views.create_article, name='create_article'),


    
    path('preview/<int:article_id>/', views.preview_article, name='preview_article'),
    path('delete/<int:article_id>/', views.delete_article, name='delete_article'),
    path('edit/<int:article_id>/', views.edit_article, name='edit_article'),  # ← ADD!
]




