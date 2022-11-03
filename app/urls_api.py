from django.urls import path

from app.views import create_paster

urlpatterns = [
    path(r'/', create_paster, name='paster-actions'),
]