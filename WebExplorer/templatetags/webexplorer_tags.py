from django import template
from MainPage.models import *

register = template.Library()


@register.inclusion_tag('MainPage/inclutions/Navigation.html')
def render_nav():
    return {'apps': Pages.objects.all()}
