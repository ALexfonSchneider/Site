from django.urls import path, include
from django.shortcuts import render, redirect

from .views import *

urlpatterns = [
    path('', RenderWebExplorerMainPage),
    path('<str:uri>/', RenderWebExplorerPage),
    path('<str:uri>/<path:system_path>/', RenderWebExplorerPage),
]