from MainPage.models import *
from django import template

register = template.Library()


@register.inclusion_tag('MainPage/inclutions/Notes.html')
def render_notes():
    return {'db': Notes.objects.all()}
