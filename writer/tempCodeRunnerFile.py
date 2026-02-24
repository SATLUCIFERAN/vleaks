def dashboard(request):    
#     if request.user.is_authenticated:
#         # Get this writer's articles
#         articles = BlogPost.objects.filter(
#             author=request.user
#         ).order_by('-created_at')
        
#         # Count published articles
#         published_count = BlogPost.objects.filter(
#             author=request.user,
#             status='published'
#         ).count()
        
#         # Count draft articles
#         draft_count = BlogPost.objects.filter(
#             author=request.user,
#             status='draft'
#         ).count()
#     else:
#         articles = []
#         published_count = 0
#         draft_count = 0
    
#     context = {
#         'articles': articles,
#         'published_count': published_count,
#         'draft_count': draft_count,
#     }
#     return render(request, 'writer/dashboard.html', context)