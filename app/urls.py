from django.urls import re_path, path

from app.views import paste_details, get_pastes

urlpatterns = [
    path('', get_pastes, name='all-pastes'),
    re_path(r'^(?P<paste_id>[\w\d]+)', paste_details, name='paste-details'),
]