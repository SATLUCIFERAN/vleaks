
from django.shortcuts import render, redirect, get_object_or_404   # ← ADD This
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from blog.models import BlogPost, Category  
from writer.models import Profile  
import os 


def validate_image(file):

    # === 1. Check file size (max 5MB) ===
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if file.size > max_size:
        return False, f'Image too large! Maximum size is 5MB.\
                        Your file: {file.size / (1024*1024):.1f}MB'
    
    # === 2. Check file extension ===
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = os.path.splitext(file.name)[1].lower()    
    if file_extension not in allowed_extensions:
        return False, f'Invalid file type! Allowed:\
               {", ".join(allowed_extensions)}. Your file: {file_extension}'
    
    # === 3. Check content type ===
    allowed_content_types = [
        'image/jpeg',
        'image/png', 
        'image/gif',
        'image/webp'
    ]    
    if file.content_type not in allowed_content_types:
        return False, f'Invalid image format! Allowed: JPEG, PNG, GIF, WebP.\
                        Your file: {file.content_type}'
    
    # All checks passed!
    return True, None


def writer_login(request):    
    if request.user.is_authenticated:
        return redirect('writer_dashboard')     
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']        
        user = authenticate(request, username=username, password=password)        
        if user is not None:            
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')            
            # Check if there's a 'next' parameter
            next_url = request.GET.get('next')      # ← ADD THIS!
            if next_url:                            # ← ADD THIS!
                return redirect(next_url)           # ← ADD THIS!
            
            return redirect('writer_dashboard')
        else:
            # Failed! Show error
            messages.error(request, 'Invalid username or password')
            return redirect('writer_login')
    
    return render(request, 'writer/login.html')

def writer_register(request):    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']        
        # List to collect all errors
        errors = []
        
        # Validation 1: Username length
        if len(username) < 3:
            errors.append('Username must be at least 3 characters')        
        # Validation 2: Username alphanumeric
        if not username.isalnum():
            errors.append('Username can only contain letters and numbers')        
        # Validation 3: Password length
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters')        
        # Validation 4: Passwords match
        if password1 != password2:
            errors.append('Passwords do not match')       
             
        # ============================================       
        # EXISTENCE CHECKS (NEW! Chapter 49)
        # ============================================        
        # Check if username already exists
        if User.objects.filter(username=username).exists():  # ← ADD THIS!
            errors.append('Username already taken')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():  # ← ADD THIS!
            errors.append('Email already registered')
        
            
        # If there are errors, show them
        if errors:
            return render(request, 'writer/register.html', {
                'errors': errors,
                'username': username,  # Keep the entered username
                'email': email,        # Keep the entered email
            })        
                
        # TODO: Check if username/email exists (Chapter 49)
        
        # ============================================
        # NO ERRORS! CREATE THE USER!
        # ============================================        
        # Create the user account
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )        
        # Show success message
        messages.success(request, f'Account created for {username}! Please login.')
        # Redirect to login page
        return redirect('writer_login')
    
    return render(request, 'writer/register.html')


@login_required  # ← ADD THIS LINE!
def dashboard(request):     
    # Get this writer's articles
    articles = BlogPost.objects.filter(
        author=request.user
    ).order_by('-created_at')    
    # Count published articles
    published_count = BlogPost.objects.filter(
        author=request.user,
        status='published'
    ).count()    
    # Count draft articles
    draft_count = BlogPost.objects.filter(
        author=request.user,
        status='draft'
    ).count()    
    # Sum total views
    total_views = BlogPost.objects.filter(
        author=request.user
    ).aggregate(Sum('views'))['views__sum'] or 0    
    context = {
        'articles': articles,
        'published_count': published_count,
        'draft_count': draft_count,
        'total_views': total_views,
    }
    return render(request, 'writer/dashboard.html', context)


def get_user_article_or_redirect(request, article_id):   
    try:
        article = BlogPost.objects.get(id=article_id)
    except BlogPost.DoesNotExist:
        messages.error(request, "Article not found!")
        return None, redirect('writer_dashboard')
    
    if article.author != request.user:
        messages.error(request, "You can only access your own articles!")
        return None, redirect('writer_dashboard')
    
    return article, None



def writer_logout(request):    
    username = request.user.username    
    logout(request)    
    messages.success(request, f'Goodbye, {username}! You\'ve left the backroom.')   
    return redirect('writer_login')



@login_required
def profile_settings(request):
    """Handle profile settings and avatar upload""" 
       
    # Get or create profile for current user
    profile, created = Profile.objects.get_or_create(user=request.user)    
    if request.method == 'POST':
        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        # Handle bio update
        if 'bio' in request.POST:
            profile.bio = request.POST['bio']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_settings')
    
    return render(request, 'writer/profile_settings.html', {
        'profile': profile
    })



@login_required
def create_article(request):    
    if request.method == 'POST':
        # Extract form data
        title = request.POST['title']
        slug = request.POST.get('slug', '')
        category_id = request.POST['category']
        content = request.POST['content']
        status = request.POST['status']        
        # Generate slug if not provided
        if not slug:
            slug = generate_slug(title)        
        
        # === Validate image if uploaded ===
        image_file = None
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            is_valid, error_message = validate_image(image_file)            
            if not is_valid:
                messages.error(request, error_message)
                # Return to form with data preserved
                categories = Category.objects.all().order_by('name')
                
                return render(request, 'writer/create_article.html', {
                    'categories': categories,
                    'title': title,
                    'slug': slug,
                    'content': content,
                    'selected_category': category_id,
                })
        
        # Create the article (without image first)
        article = BlogPost.objects.create(
            title=title,
            slug=slug,
            category_id=category_id,
            content=content,
            author=request.user,
            status=status
        )        
       
        # Save valid image
        if image_file:
            article.image = image_file
            article.save()
        
        # Success message
        if status == 'published':
            messages.success(request, f'Article "{title}" published successfully! 🎉')
        else:
            messages.success(request, f'Article "{title}" saved as draft.')        
        return redirect('writer_dashboard')    
    # GET request - show empty form
    categories = Category.objects.all().order_by('name')
    return render(request, 'writer/create_article.html', {
        'categories': categories
    })
 


from django.utils.text import slugify
import uuid

def generate_slug(title):
    """
    Generate a unique slug from title.
    Adds random suffix to ensure uniqueness.
    """
    base_slug = slugify(title)
    
    # If slug is empty (non-ASCII title), use UUID
    if not base_slug:
        base_slug = 'article'
    
    # Add short unique suffix
    unique_suffix = uuid.uuid4().hex[:6]
    
    return f"{base_slug}-{unique_suffix}"




def validate_image_magic_bytes(file):
        
    # Read first 8 bytes
    file.seek(0)
    header = file.read(8)
    file.seek(0)  # Reset for later use
    
    # Magic bytes for common image formats
    signatures = {
        b'\xff\xd8\xff': 'JPEG',
        b'\x89PNG\r\n\x1a\n': 'PNG',
        b'GIF87a': 'GIF',
        b'GIF89a': 'GIF',
        b'RIFF': 'WebP',  # WebP starts with RIFF
    }
    
    for magic, format_name in signatures.items():
        if header.startswith(magic):
            return True, format_name
    
    return False, 'Unknown format'



@login_required
def preview_article(request, article_id):    
    # Get article or 404
    article = get_object_or_404(BlogPost, id=article_id)
    
    # Only allow author to preview their own articles
    if article.author != request.user:
        messages.error(request, "You can only preview your own articles!")
        return redirect('writer_dashboard')
    
    return render(request, 'writer/preview_article.html', {
        'article': article
    })




@login_required
def delete_article(request, article_id):    
    # Get the article or 404
    article = get_object_or_404(BlogPost, id=article_id)
    
    # Security check: Only author can delete their own articles!
    if article.author != request.user:
        messages.error(request, "You can only delete your own articles!")
        return redirect('writer_dashboard')
    
    # Store title for message (before deletion)
    article_title = article.title
    
    # Delete the article
    article.delete()
    
    # Success message
    messages.success(request, f'Article "{article_title}" has been deleted.')
    
    # Redirect to dashboard
    return redirect('writer_dashboard')



@login_required
def edit_article(request, article_id):
    # Get the article or 404
    article = get_object_or_404(BlogPost, id=article_id)    
    # Security check: Only author can edit their own articles
    if article.author != request.user:
        messages.error(request, "You can only edit your own articles!")
        return redirect('writer_dashboard')
    
    # ========================================
    # HANDLE FORM SUBMISSION (POST)
    # ========================================
    if request.method == 'POST':
        # Extract form data
        title = request.POST.get('title', '').strip()
        slug = request.POST.get('slug', '').strip()
        category_id = request.POST.get('category', '')
        content = request.POST.get('content', '').strip()
        status = request.POST.get('status', 'draft')
        
        # ========================================
        # VALIDATE REQUIRED FIELDS
        # ========================================
        errors = []        
        if not title:
            errors.append('Title is required.')        
        if not category_id:
            errors.append('Please select a category.')        
        if not content:
            errors.append('Content is required.') 
       
        # ========================================
        # VALIDATE IMAGE (if uploaded)
        # ========================================
        new_image = None
        if 'image' in request.FILES:
            new_image = request.FILES['image']
            is_valid, error_message = validate_image(new_image)
            
            if not is_valid:
                errors.append(error_message)

        # If errors, show them and return to form
        if errors:
            for error in errors:
                messages.error(request, error)            
            categories = Category.objects.all().order_by('name')
            return render(request, 'writer/edit_article.html', {
                'article': article,
                'categories': categories,
            })
        
        # ========================================
        # UPDATE ARTICLE FIELDS
        # ========================================
        article.title = title
        article.category_id = category_id
        article.content = content
        article.status = status
        
        # Update slug only if changed (and not empty)
        if slug and slug != article.slug:
            # Check if new slug already exists
            if BlogPost.objects.filter(slug=slug)\
                       .exclude(id=article.id).exists():
                messages.warning(request, f'Slug "{slug}"\
                                 already exists. Keeping original.')
            else:
                article.slug = slug

        # ========================================
        # UPDATE IMAGE (if new one uploaded)
        # ========================================
        if new_image:
            # Optional: Delete old image file to save space
            if article.image:
                old_image_path = article.image.path
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Set new image
            article.image = new_image        
        
        # ========================================
        # SAVE CHANGES
        # ========================================
        article.save()
        
        # Success message
        if new_image:
            messages.success(request, f'Article "{title}" updated with new cover image!')
        else:
            messages.success(request, f'Article "{title}" updated successfully!')        
        
        # Redirect to preview page
        return redirect('preview_article', article_id=article.id)
    
    # ========================================
    # DISPLAY FORM (GET)
    # ========================================
    categories = Category.objects.all().order_by('name')
    return render(request, 'writer/edit_article.html', {
        'article': article,
        'categories': categories,
    })




