
from django import template
from django.utils.safestring import mark_safe
import bleach

register = template.Library()
# Allowed HTML tags
ALLOWED_TAGS = [
    'p', 'br', 'hr',
    'strong', 'b', 'em', 'i', 'u', 's',
    'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'a',
    'blockquote',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'figure', 'figcaption',
    'span', 'div',
]

# Allowed attributes per tag
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title'],
    'table': ['class'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
    '*': ['class'],  # Allow class on all tags
}

# Allowed URL schemes for links
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

@register.filter(name='sanitize')
def sanitize_html(value):   
    if not value:
        return ''    
    # Clean the HTML
    clean_html = bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Remove disallowed tags entirely (don't escape them)
    )    

    # Mark as safe for Django template rendering
    return mark_safe(clean_html)





