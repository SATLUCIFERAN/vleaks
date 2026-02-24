
# blog/views.py
from django.shortcuts import render
from django.http import HttpResponse

def blog_list(request):
    """
    Displays a list of blog posts
    URL: /blog/
    """
    html = f"""
    <h1>Blog List</h1>
    <h2>Request Information</h2>
    <ul>
        <li><strong>Method:</strong> {request.method}</li>
        <li><strong>Path:</strong> {request.path}</li>
        <li><strong>User:</strong> {request.user}</li>
        <li><strong>User Agent:</strong> {request.META.get('HTTP_USER_AGENT', 'Unknown')}</li>
    </ul>
    """
    return HttpResponse(html)

def blog_detail(request, id):
    """
    Displays a specific blog post
    URL: /blog/<id>/
    """
    return HttpResponse(f"<h1>Blog Post #{id}</h1><p>This is blog post number {id}.</p>")