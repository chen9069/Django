from django import template
from django.template.defaultfilters import stringfilter
import re
register = template.Library()

@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def filter(value, autoescape=None):
    ret =  re.sub(r'<a href="([^"]*\.(jpg|jpeg|pig|png|bmp))" rel="nofollow">([^"]*\.(jpg|jpeg|pig|png|bmp))</a>', r'<img src="\1"></img>', value, re.I)
    return re.sub(r'(/serve/[^"/]*)\.psg', r'<img src="\1"></img>', ret, re.I)