from django.urls import re_path, path

from app.views import gist_details

urlpatterns = [
    re_path(r'^(?P<paste_id>[\w\d]+)', gist_details, name='gist-details'),
]