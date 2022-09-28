from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from .models import *


# Create your views here.

def rendermainpage(request):
    context = {'error': request.session['error'] if 'error' in request.session else '',
               'formdata': request.session['formdata'] if 'formdata' in request.session else ''}

    return render(request, 'MainPage/main_page.html', context=context)

def createnote(request):
    try:
        content = str(request.POST['content'])

        if content.find('<script') >= 0:
            request.session['error'] = '<p style="color:red;">Ай-ай-ай! Нельзя ломать сайт! Немедленно прекрати!!!</p>'
            request.session['formdata'] = content
            return redirect('home')
        else:
            request.session['error'] = ''

        Notes.objects.create(content=content)
    finally:
        return redirect('home')


def deletenote(request):
    try:
        id = request.POST['id']

        Notes.objects.filter(id=id).delete()
    finally:
        return redirect('home')
