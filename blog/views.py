
# blog/views.py

from django.shortcuts import render, get_object_or_404  
from django.core.paginator import Paginator
from django.db.models import Sum, F  
from django.contrib.auth.models import User  
from .models import Category, BlogPost
from django.http import Http404       # ← ADD THIS!


def home(request):    
    # Featured article (most viewed published article)
    featured_article = BlogPost.objects.filter(
        status='published'
    ).order_by('-views').first()
    
    # Latest 6 articles (excluding featured if exists)
    latest_articles = BlogPost.objects.filter(
        status='published'
    ).order_by('-created_at')[:6]
    
    # All categories
    categories = Category.objects.all()
    
    # Stats
    total_articles = BlogPost.objects.filter(status='published').count()
    total_categories = Category.objects.count()
    total_views = BlogPost.objects.filter(status='published').aggregate(
        total=Sum('views')
    )['total'] or 0
    
    context = {
        'featured_article': featured_article,
        'latest_articles': latest_articles,
        'categories': categories,
        'total_articles': total_articles,
        'total_categories': total_categories,
        'total_views': total_views,
    }
    return render(request, 'blog/home.html', context)


def blog_list(request):    
    all_articles = BlogPost.objects.filter(status='published').order_by('-created_at')
    paginator = Paginator(all_articles, 5)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)         
    latest_articles = BlogPost.objects.filter(status='published').order_by('-created_at')[:3]    
    popular_articles = BlogPost.objects.filter(status='published').order_by('-views')[:5]
      
    # Recommended articles (for sidebar) 
    recommended_articles = BlogPost.objects.filter(
        status='published',
        recommended=True
    ).order_by('-created_at')[:3]
    
    # Categories (for sidebar) ← ADD THIS!
    categories = Category.objects.all()

    context = {
            'articles': articles,
            'latest_articles': latest_articles,
            'popular_articles': popular_articles,
            'recommended_articles': recommended_articles,
            'categories': categories,  # ← ADD THIS!
        }
    return render(request, 'blog/list.html', context)



def blog_detail(request, id):    
    # Get article or 404
    article = get_object_or_404(BlogPost, id=id)
    
    # Only show published articles to the public
    if article.status != 'published':
        # But allow the author to view their own drafts
        if request.user != article.author:
            raise Http404("Article not found")
    
    # Increment view count (only for published articles)
    if article.status == 'published':
        article.views = F('views') + 1
        article.save(update_fields=['views'])
        article.refresh_from_db()
    
    context = {'article': article}
    return render(request, 'blog/detail.html', context)




def category_list(request):
    categories = Category.objects.all()
    return render(request, 'blog/categories.html', {'categories': categories})


def category_articles(request, slug):    
    category = get_object_or_404(Category, slug=slug)
    
    articles = BlogPost.objects.filter(
        status='published',
        category=category
    ).order_by('-created_at')
    
    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'blog/category_articles.html', context)


def author_articles(request, username):    
    author = get_object_or_404(User, username=username)
    
    articles = BlogPost.objects.filter(
        status='published',
        author=author
    ).order_by('-created_at')
    
    context = {
        'author': author,
        'articles': articles,
    }
    return render(request, 'blog/author_articles.html', context)



