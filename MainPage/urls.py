from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', rendermainpage, name='home'),
    path('CreateNote', createnote),
    path('DeleteNote', deletenote),
    path('WebExplorer/', include('WebExplorer.urls'))
]
