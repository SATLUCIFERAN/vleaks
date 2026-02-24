
from django.contrib import admin
from .models import Category, BlogPost


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'recommended', 'views', 'created_at')
    list_filter = ('status', 'recommended', 'category', 'author')
    list_editable = ('status', 'recommended')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'







